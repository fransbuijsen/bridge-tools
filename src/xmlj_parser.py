"""Parser for XMLJ bridge files."""

import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple
import re


class BridgeHand:
    """Represents a bridge hand with card holdings for each position."""
    
    def __init__(self, north: str, east: str, south: str, west: str, 
                 dealer: str, vulnerability: str, board_number: Optional[int] = None,
                 contract: Optional[str] = None, declarer: Optional[str] = None, 
                 opening_lead: Optional[str] = None):
        self.north = north
        self.east = east
        self.south = south
        self.west = west
        self.dealer = dealer
        self.vulnerability = vulnerability
        self.board_number = board_number
        self.contract = contract
        self.declarer = declarer
        self.opening_lead = opening_lead
    
    def __repr__(self):
        contract_info = f", contract={self.contract}" if self.contract else ""
        declarer_info = f", declarer={self.declarer}" if self.declarer else ""
        lead_info = f", lead={self.opening_lead}" if self.opening_lead else ""
        return f"BridgeHand(dealer={self.dealer}, vul={self.vulnerability}, board={self.board_number}{contract_info}{declarer_info}{lead_info})"


class XMLJParser:
    """Parser for XMLJ bridge files."""
    
    @staticmethod
    def parse_auction(auction_text: str, dealer: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse auction to extract final contract and declarer."""
        if not auction_text:
            return None, None
            
        # Clean up the auction text and split into bids
        bids = auction_text.strip().split()
        
        # Remove passes and find the last actual bid
        actual_bids = [bid for bid in bids if bid not in ['P', 'PP', 'Pass', 'pass']]
        
        if not actual_bids:
            return None, None
            
        final_bid = actual_bids[-1]
        
        # Parse the contract (e.g., "7S" -> level=7, suit=S)
        contract_match = re.match(r'^(\d)([CDHSN]|NT?)$', final_bid)
        if not contract_match:
            return final_bid, None  # Return contract even if we can't parse declarer
            
        level = contract_match.group(1)
        suit = contract_match.group(2)
        
        # Normalize suit notation
        if suit == 'N':
            suit = 'NT'
        
        contract = f"{level}{suit}"
        
        # Find declarer by looking at who first bid the suit/notrump
        declarer = XMLJParser._find_declarer(bids, suit, dealer)
        
        return contract, declarer
    
    @staticmethod
    def _find_declarer(bids: list, final_suit: str, dealer: str) -> Optional[str]:
        """Find who first bid the final suit/strain."""
        # Position order starting from dealer
        positions = ['N', 'E', 'S', 'W']
        dealer_idx = positions.index(dealer)
        current_position_idx = dealer_idx
        
        # Look through bids to find first mention of the suit
        for bid in bids:
            if bid in ['P', 'PP', 'Pass', 'pass']:
                current_position_idx = (current_position_idx + 1) % 4
                continue
                
            # Check if this bid matches our final suit
            bid_match = re.match(r'^\d([CDHSN]|NT?)$', bid)
            if bid_match:
                bid_suit = bid_match.group(1)
                if bid_suit == 'N':
                    bid_suit = 'NT'
                    
                if bid_suit == final_suit:
                    # Check if current position is NS or EW partnership
                    current_pos = positions[current_position_idx]
                    if final_suit in ['C', 'D', 'S', 'H', 'NT']:
                        # For strain contracts, return the first to bid the strain in the partnership
                        if current_pos in ['N', 'S']:
                            return 'N' if current_position_idx % 2 == 0 else 'S'
                        else:
                            return 'E' if current_position_idx % 2 == 1 else 'W'
            
            current_position_idx = (current_position_idx + 1) % 4
            
        return None
    
    @staticmethod
    def parse_opening_lead(play_text: str) -> Optional[str]:
        """Parse the opening lead from the play section."""
        if not play_text:
            return None
            
        # Find the first trick
        lines = play_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('<trick>'):
                # Extract trick content: <trick> N:D3 DT DJ DK </trick>
                trick_content = line.replace('<trick>', '').replace('</trick>', '').strip()
                if ':' in trick_content:
                    # Format is like "N:D3 DT DJ DK" - the first card after : is the lead
                    cards = trick_content.split()
                    if len(cards) > 0:
                        first_card_info = cards[0]
                        if ':' in first_card_info:
                            lead_card = first_card_info.split(':')[1]
                            return lead_card
        
        return None
    
    @staticmethod
    def parse_deal_string(deal_string: str) -> Dict[str, str]:
        """
        Parse deal string format: "W:KT.A754.K542.AK5 84.98.Q93.QJ8764 AQ9653.KJ2.AT8.3 J72.QT63.J76.T92"
        Format: [Dealer]:[West] [North] [East] [South]
        Each hand: [Spades].[Hearts].[Diamonds].[Clubs]
        """
        parts = deal_string.strip().split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid deal format: {deal_string}")
        
        dealer = parts[0]
        hands = parts[1].strip().split()
        
        if len(hands) != 4:
            raise ValueError(f"Expected 4 hands, got {len(hands)}: {hands}")
        
        return {
            'dealer': dealer,
            'west': hands[0],
            'north': hands[1], 
            'east': hands[2],
            'south': hands[3]
        }
    
    @staticmethod
    def parse_xmlj_file(file_path: str) -> BridgeHand:
        """Parse an XMLJ file and return a BridgeHand object."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find the game element
            game = root.find('game')
            if game is None:
                raise ValueError("No 'game' element found in XMLJ file")
            
            # Extract deal information
            deal_elem = game.find('deal')
            if deal_elem is None:
                raise ValueError("No 'deal' element found in game")
            
            deal_string = deal_elem.text.strip()
            deal_data = XMLJParser.parse_deal_string(deal_string)
            
            # Extract other game information
            dealer_elem = game.find('dealer')
            dealer = dealer_elem.text.strip() if dealer_elem is not None else deal_data['dealer']
            
            vul_elem = game.find('vul')
            vulnerability = vul_elem.text.strip() if vul_elem is not None else 'None'
            
            board_elem = game.find('boardnr')
            board_number = None
            if board_elem is not None and board_elem.text:
                try:
                    board_number = int(board_elem.text.strip())
                except ValueError:
                    pass
            
            # Extract auction information
            contract = None
            declarer = None
            auction_elem = game.find('auction')
            if auction_elem is not None:
                bids_elem = auction_elem.find('bids')
                if bids_elem is not None and bids_elem.text:
                    auction_text = bids_elem.text.strip()
                    contract, declarer = XMLJParser.parse_auction(auction_text, dealer)
            
            # Extract opening lead from play
            opening_lead = None
            play_elem = game.find('play')
            if play_elem is not None:
                # Get all the trick text content
                play_text = ET.tostring(play_elem, encoding='unicode')
                opening_lead = XMLJParser.parse_opening_lead(play_text)
            
            return BridgeHand(
                north=deal_data['north'],
                east=deal_data['east'],
                south=deal_data['south'],
                west=deal_data['west'],
                dealer=dealer,
                vulnerability=vulnerability,
                board_number=board_number,
                contract=contract,
                declarer=declarer,
                opening_lead=opening_lead
            )
            
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML file: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing XMLJ file: {e}")

