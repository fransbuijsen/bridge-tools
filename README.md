# bridge-tools
A collection of tools for analysing the game of bridge

## Bridge Hand Analyzer

A Python tool that parses bridge hands from XMLJ files and feeds them to a Double Dummy Solver (DDS) web service for analysis.

### Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Basic usage (opens DDS analysis in your browser automatically):
```bash
python bridge_analyzer.py Source/20250517-dt-wc.xmlj
```

Verbose output (shows all extracted information before opening):
```bash
python bridge_analyzer.py --verbose Source/20250517-dt-wc.xmlj
```

Just get the URL (without opening browser):
```bash
python bridge_analyzer.py --output url Source/20250517-dt-wc.xmlj
```

Fetch the actual HTML analysis (raw HTML output):
```bash
python bridge_analyzer.py --output html Source/20250517-dt-wc.xmlj
```

### Options

- `--output, -o`: Output format: 'open' (default - opens in browser), 'url' (just print URL), or 'html' (fetch HTML content)
- `--verbose, -v`: Show detailed parsing information

### Auto-Extracted Information

The tool automatically extracts the following from your XMLJ file:
- **Contract**: Determined from the auction sequence (final bid)
- **Declarer**: Calculated based on who first bid the trump suit/strain
- **Opening Lead**: Taken from the first card played in the trick sequence
- **Vulnerability**: From the `<vul>` element
- **Dealer**: From the `<dealer>` element
- **Board Number**: From the `<boardnr>` element

### File Format

The tool expects XMLJ files with the following structure:
```xml
<document>
  <game>
    <auction>
      <bids> 1N PP 2H PP 2S PP 4C PP 4D PP 4H PP 4S PP 4N PP 5C PP 5H PP 6C PP 7S PP PP PP </bids>
    </auction>
    <deal>W:KT.A754.K542.AK5 84.98.Q93.QJ8764 AQ9653.KJ2.AT8.3 J72.QT63.J76.T92</deal>
    <dealer>W</dealer>
    <vul>EW</vul>
    <boardnr>16</boardnr>
    <play>
      <trick> N:D3 DT DJ DK </trick>
      <!-- more tricks... -->
    </play>
  </game>
</document>
```

**Data Formats:**
- **Deal**: `[Dealer]:[West] [North] [East] [South]`
- **Hand**: `[Spades].[Hearts].[Diamonds].[Clubs]`
- **Auction**: Space-separated bids, with PP for pass
- **Tricks**: Format like `N:D3 DT DJ DK` (leader:card1 card2 card3 card4)
