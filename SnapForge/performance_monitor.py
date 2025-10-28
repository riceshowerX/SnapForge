"""
性能监控和调试工具模块
提供全面的性能监控、资源跟踪和调试功能
"""

import time
import psutil
import logging
import functools
import threading
import gc
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class PerformanceLevel(Enum):
    """性能级别枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    function_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    timestamp: float
    success: bool
    error_message: Optional[str] = None
    input_size: Optional[int] = None
    output_size: Optional[int] = None


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    timestamp: float
    memory_total_mb: float
    memory_used_mb: float
    memory_percent: float
    cpu_percent: float
    disk_usage_percent: float
    active_threads: int


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_records: int = 1000):
        self.logger = logging.getLogger("PerformanceMonitor")
        self.performance_records: List[PerformanceMetrics] = []
        self.system_records: List[SystemMetrics] = []
        self.max_records = max_records
        self._lock = threading.Lock()
        self._enabled = True
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        # 性能阈值配置
        self.thresholds = {
            'execution_time_warning': 5.0,  # 5秒警告
            'execution_time_critical': 30.0,  # 30秒严重
            'memory_warning_mb': 500,  # 500MB警告
            'memory_critical_mb': 1000,  # 1000MB严重
            'cpu_warning_percent': 80,  # 80%警告
            'cpu_critical_percent': 95,  # 95%严重
        }
    
    def monitor_function(self, track_memory: bool = True, track_cpu: bool = True):
        """函数性能监控装饰器"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)
                
                # 记录开始时间和资源使用
                start_time = time.time()
                start_memory = self._get_process_memory_mb() if track_memory else 0
                start_cpu = psutil.cpu_percent(interval=None) if track_cpu else 0
                
                # 估算输入大小（如果可能）
                input_size = self._estimate_input_size(args, kwargs)
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # 计算资源使用
                    end_memory = self._get_process_memory_mb() if track_memory else 0
                    end_cpu = psutil.cpu_percent(interval=None) if track_cpu else 0
                    
                    memory_usage = end_memory - start_memory if track_memory else 0
                    cpu_usage = end_cpu - start_cpu if track_cpu else 0
                    
                    # 估算输出大小
                    output_size = self._estimate_output_size(result)
                    
                    # 记录性能指标
                    metrics = PerformanceMetrics(
                        function_name=func.__name__,
                        execution_time=execution_time,
                        memory_usage_mb=memory_usage,
                        cpu_percent=cpu_usage,
                        timestamp=start_time,
                        success=True,
                        input_size=input_size,
                        output_size=output_size
                    )
                    
                    self._add_performance_record(metrics)
                    self._check_performance_thresholds(metrics)
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    # 记录错误性能指标
                    metrics = PerformanceMetrics(
                        function_name=func.__name__,
                        execution_time=execution_time,
                        memory_usage_mb=0,
                        cpu_percent=0,
                        timestamp=start_time,
                        success=False,
                        error_message=str(e),
                        input_size=input_size
                    )
                    
                    self._add_performance_record(metrics)
                    self.logger.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def record_system_metrics(self):
        """记录系统级性能指标"""
        if not self._enabled:
            return
        
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            disk = psutil.disk_usage('/')
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                memory_total_mb=memory.total / 1024 / 1024,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_percent=memory.percent,
                cpu_percent=cpu,
                disk_usage_percent=disk.percent,
                active_threads=threading.active_count()
            )
            
            with self._lock:
                self.system_records.append(metrics)
                if len(self.system_records) > self.max_records:
                    self.system_records.pop(0)
                    
            # 检查系统资源警告
            self._check_system_thresholds(metrics)
            
        except Exception as e:
            self.logger.warning(f"Failed to record system metrics: {e}")
    
    def get_performance_summary(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """获取性能摘要"""
        with self._lock:
            records = self.performance_records
            if function_name:
                records = [r for r in records if r.function_name == function_name]
            
            if not records:
                return {}
            
            successful_records = [r for r in records if r.success]
            failed_records = [r for r in records if not r.success]
            
            summary = {
                'total_calls': len(records),
                'successful_calls': len(successful_records),
                'failed_calls': len(failed_records),
                'success_rate': len(successful_records) / len(records) if records else 0,
                'avg_execution_time': sum(r.execution_time for r in successful_records) / len(successful_records) if successful_records else 0,
                'max_execution_time': max(r.execution_time for r in successful_records) if successful_records else 0,
                'avg_memory_usage': sum(r.memory_usage_mb for r in successful_records) / len(successful_records) if successful_records else 0,
                'max_memory_usage': max(r.memory_usage_mb for r in successful_records) if successful_records else 0,
                'recent_calls': [
                    {
                        'function': r.function_name,
                        'time': r.execution_time,
                        'memory': r.memory_usage_mb,
                        'success': r.success,
                        'timestamp': r.timestamp
                    } for r in records[-10:]  # 最近10次调用
                ]
            }
            
            return summary
    
    def get_system_summary(self) -> Dict[str, Any]:
        """获取系统摘要"""
        with self._lock:
            if not self.system_records:
                return {}
            
            latest = self.system_records[-1]
            
            # 计算最近10次记录的平均值
            recent_records = self.system_records[-10:]
            
            summary = {
                'current': {
                    'memory_percent': latest.memory_percent,
                    'cpu_percent': latest.cpu_percent,
                    'disk_usage_percent': latest.disk_usage_percent,
                    'active_threads': latest.active_threads,
                    'timestamp': latest.timestamp
                },
                'averages': {
                    'memory_percent': sum(r.memory_percent for r in recent_records) / len(recent_records),
                    'cpu_percent': sum(r.cpu_percent for r in recent_records) / len(recent_records),
                    'disk_usage_percent': sum(r.disk_usage_percent for r in recent_records) / len(recent_records)
                },
                'trend': self._analyze_system_trend()
            }
            
            return summary
    
    def enable_monitoring(self):
        """启用监控"""
        self._enabled = True
        self.logger.info("Performance monitoring enabled")
    
    def disable_monitoring(self):
        """禁用监控"""
        self._enabled = False
        self.logger.info("Performance monitoring disabled")
    
    def clear_records(self):
        """清除所有记录"""
        with self._lock:
            self.performance_records.clear()
            self.system_records.clear()
        self.logger.info("Performance records cleared")
    
    def start_monitoring(self):
        """开始监控"""
        self._enabled = True
        
        # 启动后台监控线程
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._stop_monitoring.clear()
            self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitoring_thread.start()
            self.logger.info("Performance monitoring started with background thread")
        else:
            self.logger.info("Performance monitoring already running")
    
    def stop_monitoring(self):
        """停止监控"""
        self._enabled = False
        
        # 停止后台监控线程
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)
            self.logger.info("Performance monitoring stopped")
        else:
            self.logger.info("Performance monitoring was not running")
    
    def reset_data(self):
        """重置数据"""
        self.clear_records()
        self.logger.info("Performance data reset")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        if not self.system_records:
            return {}
        
        latest_system = self.system_records[-1]
        
        # 获取最近的处理时间
        latest_processing_time = 0
        if self.performance_records:
            latest_processing_time = self.performance_records[-1].execution_time
        
        return {
            'memory_percent': latest_system.memory_percent,
            'cpu_percent': latest_system.cpu_percent,
            'disk_percent': latest_system.disk_usage_percent,
            'processing_time': latest_processing_time,
            'active_threads': latest_system.active_threads,
            'timestamp': latest_system.timestamp
        }
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取历史数据"""
        history = []
        for record in self.system_records[-50:]:  # 最近50条记录
            history.append({
                'timestamp': record.timestamp,
                'memory_percent': record.memory_percent,
                'cpu_percent': record.cpu_percent,
                'disk_percent': record.disk_usage_percent
            })
        return history
    
    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        
        if not self.system_records:
            return ["系统监控数据不足，无法提供优化建议"]
        
        latest_system = self.system_records[-1]
        
        # 内存使用建议
        if latest_system.memory_percent > 80:
            suggestions.append("内存使用率较高，建议优化图片处理的内存使用或增加系统内存")
        
        # CPU使用建议
        if latest_system.cpu_percent > 80:
            suggestions.append("CPU使用率较高，建议减少并发处理任务或优化处理算法")
        
        # 磁盘使用建议
        if latest_system.disk_usage_percent > 90:
            suggestions.append("磁盘空间不足，建议清理临时文件或增加磁盘空间")
        
        # 处理时间建议
        if self.performance_records:
            recent_times = [r.execution_time for r in self.performance_records[-10:] if r.success]
            if recent_times and max(recent_times) > 10:
                suggestions.append("部分处理任务耗时较长，建议优化处理逻辑或分批处理")
        
        if not suggestions:
            suggestions.append("系统性能良好，暂无优化建议")
        
        return suggestions
    
    def _monitoring_loop(self):
        """后台监控循环"""
        while not self._stop_monitoring.is_set():
            try:
                # 记录系统指标
                self.record_system_metrics()
                
                # 每5秒记录一次
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(1)  # 出错后等待1秒再继续

    def _get_process_memory_mb(self) -> float:
        """获取当前进程内存使用（MB）"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def _estimate_input_size(self, args: tuple, kwargs: dict) -> Optional[int]:
        """估算输入数据大小"""
        try:
            size = 0
            for arg in args:
                if hasattr(arg, '__len__'):
                    size += len(str(arg))
            for key, value in kwargs.items():
                size += len(str(key)) + len(str(value))
            return size if size > 0 else None
        except Exception:
            return None
    
    def _estimate_output_size(self, result) -> Optional[int]:
        """估算输出数据大小"""
        try:
            if hasattr(result, '__len__'):
                return len(str(result))
            return None
        except Exception:
            return None
    
    def _add_performance_record(self, metrics: PerformanceMetrics):
        """添加性能记录"""
        with self._lock:
            self.performance_records.append(metrics)
            if len(self.performance_records) > self.max_records:
                self.performance_records.pop(0)
    
    def _check_performance_thresholds(self, metrics: PerformanceMetrics):
        """检查性能阈值并记录警告"""
        if metrics.execution_time > self.thresholds['execution_time_critical']:
            self.logger.critical(
                f"Critical performance issue in {metrics.function_name}: "
                f"Execution time {metrics.execution_time:.2f}s exceeds critical threshold"
            )
        elif metrics.execution_time > self.thresholds['execution_time_warning']:
            self.logger.warning(
                f"Performance warning in {metrics.function_name}: "
                f"Execution time {metrics.execution_time:.2f}s exceeds warning threshold"
            )
        
        if metrics.memory_usage_mb > self.thresholds['memory_critical_mb']:
            self.logger.critical(
                f"Critical memory usage in {metrics.function_name}: "
                f"Memory usage {metrics.memory_usage_mb:.2f}MB exceeds critical threshold"
            )
        elif metrics.memory_usage_mb > self.thresholds['memory_warning_mb']:
            self.logger.warning(
                f"Memory warning in {metrics.function_name}: "
                f"Memory usage {metrics.memory_usage_mb:.2f}MB exceeds warning threshold"
            )
    
    def _check_system_thresholds(self, metrics: SystemMetrics):
        """检查系统阈值"""
        if metrics.memory_percent > self.thresholds['cpu_critical_percent']:
            self.logger.critical(f"Critical system memory usage: {metrics.memory_percent:.1f}%")
        elif metrics.memory_percent > self.thresholds['cpu_warning_percent']:
            self.logger.warning(f"High system memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.cpu_percent > self.thresholds['cpu_critical_percent']:
            self.logger.critical(f"Critical system CPU usage: {metrics.cpu_percent:.1f}%")
        elif metrics.cpu_percent > self.thresholds['cpu_warning_percent']:
            self.logger.warning(f"High system CPU usage: {metrics.cpu_percent:.1f}%")
    
    def _analyze_system_trend(self) -> str:
        """分析系统趋势"""
        if len(self.system_records) < 2:
            return "insufficient_data"
        
        recent = self.system_records[-5:]
        first = recent[0]
        last = recent[-1]
        
        memory_diff = last.memory_percent - first.memory_percent
        cpu_diff = last.cpu_percent - first.cpu_percent
        
        if memory_diff > 5 or cpu_diff > 5:
            return "increasing"
        elif memory_diff < -5 or cpu_diff < -5:
            return "decreasing"
        else:
            return "stable"


class DebugHelper:
    """调试助手类"""
    
    def __init__(self):
        self.logger = logging.getLogger("DebugHelper")
    
    def memory_snapshot(self) -> Dict[str, Any]:
        """内存快照"""
        try:
            import gc
            
            # 强制垃圾回收
            gc.collect()
            
            # 获取内存信息
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # 获取对象计数
            objects = gc.get_objects()
            object_counts = {}
            for obj in objects:
                obj_type = type(obj).__name__
                object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
            
            # 按数量排序
            sorted_counts = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'memory_rss_mb': memory_info.rss / 1024 / 1024,
                'memory_vms_mb': memory_info.vms / 1024 / 1024,
                'total_objects': len(objects),
                'top_object_types': sorted_counts[:10],  # 前10种对象类型
                'gc_generation_counts': [len(gc.get_objects(i)) for i in range(3)]
            }
            
        except Exception as e:
            self.logger.error(f"Memory snapshot failed: {e}")
            return {}
    
    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """函数性能分析"""
        import cProfile
        import pstats
        import io
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
        
        # 分析性能数据
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # 显示前10个最耗时的函数
        
        profile_output = s.getvalue()
        
        return {
            'result': result,
            'profile_summary': profile_output,
            'function_name': func.__name__
        }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """检查依赖包状态"""
        dependencies = {
            'PIL (Pillow)': True,  # 假设已安装
            'psutil': self._check_module('psutil'),
            'numpy': self._check_module('numpy'),
            'matplotlib': self._check_module('matplotlib'),
            'imagehash': self._check_module('imagehash'),
            'piexif': self._check_module('piexif'),
            'colorthief': self._check_module('colorthief'),
        }
        
        return dependencies
    
    def _check_module(self, module_name: str) -> bool:
        """检查模块是否可用"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def take_memory_snapshot(self) -> Dict[str, Any]:
        """获取内存快照（兼容app.py中的调用）"""
        return self.memory_snapshot()
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            import platform
            
            # 获取系统信息
            system_info = {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'architecture': platform.architecture(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'python_implementation': platform.python_implementation(),
            }
            
            # 获取内存信息
            memory = psutil.virtual_memory()
            system_info.update({
                'memory_total_gb': memory.total / 1024 / 1024 / 1024,
                'memory_available_gb': memory.available / 1024 / 1024 / 1024,
                'memory_used_percent': memory.percent,
            })
            
            # 获取CPU信息
            cpu_info = {
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'cpu_frequency': psutil.cpu_freq(),
            }
            system_info.update(cpu_info)
            
            # 获取磁盘信息
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        'total_gb': usage.total / 1024 / 1024 / 1024,
                        'used_gb': usage.used / 1024 / 1024 / 1024,
                        'free_gb': usage.free / 1024 / 1024 / 1024,
                        'percent': usage.percent
                    }
                except Exception:
                    continue
            
            system_info['disk_partitions'] = disk_info
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {'error': str(e)}


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()
debug_helper = DebugHelper()

# 便捷装饰器
def monitor_performance(track_memory=True, track_cpu=True):
    """便捷的性能监控装饰器"""
    return performance_monitor.monitor_function(track_memory, track_cpu)


def get_performance_dashboard() -> Dict[str, Any]:
    """获取性能仪表板数据"""
    return {
        'function_performance': performance_monitor.get_performance_summary(),
        'system_metrics': performance_monitor.get_system_summary(),
        'memory_snapshot': debug_helper.memory_snapshot(),
        'dependencies': debug_helper.check_dependencies()
    }