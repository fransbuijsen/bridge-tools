#!/usr/bin/env python3
"""Main CLI tool for bridge hand analysis."""

import click
import sys
from pathlib import Path

from .xmlj_parser import XMLJParser
from .dds_client import DDSClient


@click.command()
@click.argument('xmlj_file', type=click.Path(exists=True, path_type=Path))
@click.option('--contract', '-c', help='Contract to analyze (e.g., 4S, 3NT)')
@click.option('--declarer', '-d', help='Declarer (N, E, S, W)')
@click.option('--lead', '-l', help='Opening lead (e.g., H3, SA)')
@click.option('--output', '-o', type=click.Choice(['url', 'html']), default='url',
              help='Output format: url (just the URL) or html (fetch the page)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(xmlj_file, contract, declarer, lead, output, verbose):
    """Analyze a bridge hand from an XMLJ file using Double Dummy Solver."""
    
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
            click.echo()
        
        # Create DDS client and generate analysis
        dds = DDSClient()
        
        if output == 'url':
            url = dds.analyze_hand(hand, contract, declarer, lead)
            click.echo(url)
        
        elif output == 'html':
            if verbose:
                click.echo("Fetching DDS analysis...")
            
            try:
                html_content = dds.get_analysis_page(hand, contract, declarer, lead)
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

