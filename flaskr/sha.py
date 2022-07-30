from typing import Optional, List
from datetime import datetime

from dataclasses import dataclass


@dataclass
class ServiceDisruption:
    """ Class representing a SHA service disruption
    """

    start_date: Optional[str] # Datetime ISO string
    end_date: Optional[str] # Datetime ISO string

    title: Optional[str]
    link: Optional[str]

    facility_name: Optional[str]
    community_name: Optional[str]
    region_name: Optional[str]

    disruption: Optional[str]


@dataclass
class ServiceDisruptionsPage:
    """ Class representing a page of SHA service disruptions. 
    """
    disruptions: List[ServiceDisruption]

    # link to next page of disruptions
    next: Optional[str]
