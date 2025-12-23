from phoenix_engine.core.config import ChartConfig


class ChartFactory:
    """
    Central pipeline factory.
    """

    @staticmethod
    def create_chart(dt, lat, lon):
        """
        Helper hook for TajakaEngine. Implementation can be added when a lightweight
        chart generator is available.
        """
        from phoenix_engine.engines.birth import BirthChartEngine

        cfg = ChartConfig()
        engine = BirthChartEngine(cfg)
        return engine.calculate_natal_chart(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=getattr(dt, "second", 0),
            lat=lat,
            lon=lon,
            name="AutoChart",
        )

    @staticmethod
    def create_pipeline(pipeline_type: str, config: ChartConfig):
        """
        Build processing pipeline based on type.
        Imports are inside to avoid import cycles.
        """
        from phoenix_engine.plugins.birth_plugin import BirthChartPlugin
        from phoenix_engine.plugins.transit_plugin import TransitAnalysisPlugin
        from phoenix_engine.plugins.tajaka_plugin import TajakaPlugin

        pipeline = []

        if pipeline_type == "BIRTH":
            pipeline.append(BirthChartPlugin(config))

        elif pipeline_type == "TRANSIT":
            pipeline.append(BirthChartPlugin(config))
            pipeline.append(TransitAnalysisPlugin(config))

        elif pipeline_type == "ANNUAL":
            pipeline.append(BirthChartPlugin(config))
            pipeline.append(TajakaPlugin(config))

        return pipeline
