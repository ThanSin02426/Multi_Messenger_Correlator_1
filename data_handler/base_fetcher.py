from abc import ABC, abstractmethod
import pandas as pd

class BaseFetcher(ABC):
    """
    Abstract Base Class for all data fetchers.
    
    Each child class must implement the `fetch` method, which should return a
    pandas DataFrame with the following standardized columns:
    - 'event_id': A unique identifier for the event.
    - 'source': The name of the observatory/messenger type (e.g., 'GWOSC', 'ZTF').
    - 'astropy_time': An astropy.time.Time object for the event time.
    - 'astropy_coord': An astropy.coordinates.SkyCoord object for the position.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """
        Fetches event data and returns it in a standardized DataFrame format.
        """
        pass

    def __str__(self) -> str:
        return f"<{self.name} Fetcher>"