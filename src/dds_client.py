"""Double Dummy Solver client for interfacing with web-based DDS."""

import requests
from urllib.parse import urlencode
from typing import Optional

from xmlj_parser import BridgeHand


class DDSClient:
    """Client for interfacing with the Double Dummy Solver web service."""
    
    def __init__(self, base_url: str = "https://dds.bridgewebs.com/bsol2/ddummy.htm"):
        self.base_url = base_url
    
    def _convert_vulnerability(self, vul: str) -> str:
        """Convert vulnerability format to DDS format."""
        vul_map = {
            'None': 'None',
            'NS': 'NS', 
            'EW': 'EW',
            'All': 'All',
            'Both': 'All'
        }
        return vul_map.get(vul, 'None')
    
    def build_dds_url(self, hand: BridgeHand, contract: Optional[str] = None, 
                     declarer: Optional[str] = None, lead: Optional[str] = None,
                     club: str = "stepbridge_nl", analyse: bool = True) -> str:
        """Build the DDS URL from a BridgeHand object."""
        
        params = {
            'club': club,
            'north': hand.north,
            'east': hand.east, 
            'south': hand.south,
            'west': hand.west,
            'dealer': hand.dealer,
            'vul': self._convert_vulnerability(hand.vulnerability),
            'analyse': 'true' if analyse else 'false'
        }
        
        # Add board number if available
        if hand.board_number is not None:
            params['board'] = str(hand.board_number)
        
        # Add contract information if provided
        if contract:
            params['contract'] = contract
        if declarer:
            params['declarer'] = declarer
        if lead:
            params['lead'] = lead
            
        # Add title
        params['title'] = '<h1>StepBridge <b>Double</b> Dummy Analysis</h1>'
        
        return f"{self.base_url}?{urlencode(params)}"
    
    def analyze_hand(self, hand: BridgeHand, contract: Optional[str] = None,
                    declarer: Optional[str] = None, lead: Optional[str] = None) -> str:
        """Generate DDS analysis URL for a bridge hand."""
        return self.build_dds_url(hand, contract, declarer, lead)
    
    def get_analysis_page(self, hand: BridgeHand, contract: Optional[str] = None,
                         declarer: Optional[str] = None, lead: Optional[str] = None) -> str:
        """Fetch the actual DDS analysis page content."""
        url = self.build_dds_url(hand, contract, declarer, lead)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch DDS analysis: {e}")

