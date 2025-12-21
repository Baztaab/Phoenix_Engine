
from abc import ABC, abstractmethod
from phoenix_engine.core.context import ChartContext

class IChartPlugin(ABC):
    "قرارداد کلی تمام پلاگین‌های محاسباتی"
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, context: ChartContext):
        "اجرای منطق و پر کردن context.analysis"
        pass
