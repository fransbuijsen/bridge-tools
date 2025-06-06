#!/usr/bin/env python3
"""CLI entry point for bridge analyzer."""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from xmlj_parser import XMLJParser
from dds_client import DDSClient

import click
from pathlib import Path
import webbrowser


@click.command()
@click.argument('xmlj_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Choice(['url', 'html', 'open']), default='open',
              help='Output format: url (just the URL), html (fetch the page), or open (open in browser)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(xmlj_file, output, verbose):
    """Analyze a bridge hand from an XMLJ file using Double Dummy Solver.
    
    All parameters (contract, declarer, opening lead) are automatically
    extracted from the XMLJ file's auction and play data.
    """
    
    try:
        # Parse the XMLJ file
        if verbose:
            click.echo(f"Parsing XMLJ file: {xmlj_file}")
        
        hand = XMLJParser.parse_xmlj_file(str(xmlj_file))
        
        if verbose:
            click.echo(f"Parsed hand: {hand}")
            click.echo(f"North: {hand.north}")
            click.echo(f"East:  {hand.east}")
            click.echo(f"South: {hand.south}")
            click.echo(f"West:  {hand.west}")
            click.echo(f"Dealer: {hand.dealer}, Vulnerability: {hand.vulnerability}")
            if hand.board_number:
                click.echo(f"Board: {hand.board_number}")
            if hand.contract:
                click.echo(f"Contract: {hand.contract}")
            if hand.declarer:
                click.echo(f"Declarer: {hand.declarer}")
            if hand.opening_lead:
                click.echo(f"Opening Lead: {hand.opening_lead}")
            click.echo()
        
        # Create DDS client and generate analysis
        dds = DDSClient()
        
        # Generate the DDS URL
        url = dds.analyze_hand(hand, hand.contract, hand.declarer, hand.opening_lead)
        
        if output == 'url':
            click.echo(url)
        
        elif output == 'open':
            if verbose:
                click.echo(f"Opening URL in browser: {url}")
            try:
                webbrowser.open(url)
                click.echo("DDS analysis opened in your default browser.")
            except Exception as e:
                click.echo(f"Error opening browser: {e}", err=True)
                click.echo(f"URL: {url}")
        
        elif output == 'html':
            if verbose:
                click.echo("Fetching DDS analysis...")
            
            try:
                html_content = dds.get_analysis_page(hand, hand.contract, hand.declarer, hand.opening_lead)
                click.echo(html_content)
            except RuntimeError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
        
    except ValueError as e:
        click.echo(f"Error parsing XMLJ file: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    analyze()

