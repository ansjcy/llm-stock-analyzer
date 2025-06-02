"""
Token Usage Tracker for LLM API calls
Tracks token usage, costs, and provides detailed reporting
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.utils.logger import stock_logger


@dataclass
class TokenUsage:
    """Track token usage for a single LLM call"""
    provider: str
    model: str
    operation: str  # e.g., 'technical_analysis', 'fundamental_analysis'
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0  # For Gemini cached content
    timestamp: float = field(default_factory=time.time)
    duration_seconds: float = 0.0
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    @property
    def billable_input_tokens(self) -> int:
        """Input tokens that are actually billed (excluding cached)"""
        return max(0, self.input_tokens - self.cached_tokens)


class TokenTracker:
    """Track and report token usage across LLM API calls"""
    
    # Current pricing per 1M tokens (as of January 2025)
    # Updated: January 2025 - Added Gemini 2.5 Flash Preview pricing
    # Source: https://ai.google.dev/gemini-api/docs/pricing
    PRICING = {
        'openai': {
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4': {'input': 30.00, 'output': 60.00},
            'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        },
        'gemini': {
            # Gemini 2.5 series (Preview models)
            'gemini-2.5-flash-preview-05-20': {'input': 0.15, 'output': 0.60},
            'gemini-2.5-flash-preview': {'input': 0.15, 'output': 0.60},  # Generic alias
            'gemini-2.5-pro-preview': {'input': 1.25, 'output': 10.00},  # For <= 200k tokens
            # Gemini 2.0 series
            'gemini-2.0-flash': {'input': 0.075, 'output': 0.40},
            'gemini-2.0-flash-lite': {'input': 0.075, 'output': 0.30},
            # Gemini 1.5 series
            'gemini-1.5-flash': {'input': 0.075, 'output': 0.30},
            'gemini-1.5-flash-8b': {'input': 0.0375, 'output': 0.15},
            'gemini-1.5-pro': {'input': 1.25, 'output': 5.00},
            # Legacy models
            'gemini-1.0-pro': {'input': 0.50, 'output': 1.50},
        }
    }
    
    def __init__(self):
        self.usage_records: List[TokenUsage] = []
        self.start_time = time.time()
        self.console = Console()
        
    def record_usage(self, provider: str, model: str, operation: str, 
                    input_tokens: int, output_tokens: int, 
                    cached_tokens: int = 0, duration_seconds: float = 0.0) -> None:
        """Record token usage for an LLM call"""
        usage = TokenUsage(
            provider=provider.lower(),
            model=model.lower(),
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            duration_seconds=duration_seconds
        )
        
        self.usage_records.append(usage)
        
        # Log the usage
        cost = self.calculate_cost(usage)
        cost_str = f"${cost:.4f}" if cost > 0 else "N/A"
        
        stock_logger.info(
            f"Token usage - {operation}: {input_tokens} input + {output_tokens} output = "
            f"{usage.total_tokens} total tokens ({provider}/{model}) - Cost: {cost_str}"
        )
        
        # Display usage information
        self._display_call_usage(usage, cost)
    
    def calculate_cost(self, usage: TokenUsage) -> float:
        """Calculate cost for a token usage record"""
        provider_pricing = self.PRICING.get(usage.provider, {})
        model_pricing = provider_pricing.get(usage.model, {})
        
        if not model_pricing:
            return 0.0
        
        input_cost = (usage.billable_input_tokens / 1_000_000) * model_pricing.get('input', 0)
        output_cost = (usage.output_tokens / 1_000_000) * model_pricing.get('output', 0)
        
        return input_cost + output_cost
    
    def _display_call_usage(self, usage: TokenUsage, cost: float) -> None:
        """Display usage information for a single call"""
        cached_info = f" (cached: {usage.cached_tokens})" if usage.cached_tokens > 0 else ""
        cost_info = f" - ${cost:.4f}" if cost > 0 else ""
        duration_info = f" - {usage.duration_seconds:.1f}s" if usage.duration_seconds > 0 else ""
        
        self.console.print(
            f"[dim]  → {usage.operation}: {usage.input_tokens} input + {usage.output_tokens} output "
            f"= {usage.total_tokens} tokens{cached_info}{cost_info}{duration_info}[/dim]"
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary"""
        if not self.usage_records:
            return {
                'total_calls': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'by_provider': {},
                'by_operation': {},
                'duration_seconds': time.time() - self.start_time
            }
        
        total_tokens = sum(usage.total_tokens for usage in self.usage_records)
        total_cost = sum(self.calculate_cost(usage) for usage in self.usage_records)
        
        # Group by provider
        by_provider = {}
        for usage in self.usage_records:
            if usage.provider not in by_provider:
                by_provider[usage.provider] = {
                    'calls': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'cached_tokens': 0,
                    'total_tokens': 0,
                    'cost': 0.0,
                    'models': set()
                }
            
            provider_stats = by_provider[usage.provider]
            provider_stats['calls'] += 1
            provider_stats['input_tokens'] += usage.input_tokens
            provider_stats['output_tokens'] += usage.output_tokens
            provider_stats['cached_tokens'] += usage.cached_tokens
            provider_stats['total_tokens'] += usage.total_tokens
            provider_stats['cost'] += self.calculate_cost(usage)
            provider_stats['models'].add(usage.model)
        
        # Convert sets to lists for JSON serialization
        for provider_stats in by_provider.values():
            provider_stats['models'] = list(provider_stats['models'])
        
        # Group by operation
        by_operation = {}
        for usage in self.usage_records:
            if usage.operation not in by_operation:
                by_operation[usage.operation] = {
                    'calls': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'total_tokens': 0,
                    'cost': 0.0
                }
            
            op_stats = by_operation[usage.operation]
            op_stats['calls'] += 1
            op_stats['input_tokens'] += usage.input_tokens
            op_stats['output_tokens'] += usage.output_tokens
            op_stats['total_tokens'] += usage.total_tokens
            op_stats['cost'] += self.calculate_cost(usage)
        
        return {
            'total_calls': len(self.usage_records),
            'total_input_tokens': sum(usage.input_tokens for usage in self.usage_records),
            'total_output_tokens': sum(usage.output_tokens for usage in self.usage_records),
            'total_cached_tokens': sum(usage.cached_tokens for usage in self.usage_records),
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'by_provider': by_provider,
            'by_operation': by_operation,
            'duration_seconds': time.time() - self.start_time,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.now().isoformat()
        }


    def display_summary(self) -> None:
        """Display a comprehensive usage summary"""
        summary = self.get_summary()

        if summary['total_calls'] == 0:
            self.console.print("[yellow]No LLM API calls were made during this run.[/yellow]")
            return

        # Main summary table
        summary_table = Table(title="🔢 Token Usage Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total API Calls", str(summary['total_calls']))
        summary_table.add_row("Input Tokens", f"{summary['total_input_tokens']:,}")
        summary_table.add_row("Output Tokens", f"{summary['total_output_tokens']:,}")
        if summary['total_cached_tokens'] > 0:
            summary_table.add_row("Cached Tokens", f"{summary['total_cached_tokens']:,}")
        summary_table.add_row("Total Tokens", f"{summary['total_tokens']:,}")
        summary_table.add_row("Total Cost", f"${summary['total_cost']:.4f}")
        summary_table.add_row("Duration", f"{summary['duration_seconds']:.1f} seconds")

        self.console.print(summary_table)

        # Provider breakdown
        if summary['by_provider']:
            provider_table = Table(title="📊 Usage by Provider")
            provider_table.add_column("Provider", style="cyan")
            provider_table.add_column("Models", style="dim")
            provider_table.add_column("Calls", style="yellow")
            provider_table.add_column("Input", style="blue")
            provider_table.add_column("Output", style="green")
            provider_table.add_column("Total", style="magenta")
            provider_table.add_column("Cost", style="red")

            for provider, stats in summary['by_provider'].items():
                models_str = ", ".join(stats['models'])
                provider_table.add_row(
                    provider.upper(),
                    models_str,
                    str(stats['calls']),
                    f"{stats['input_tokens']:,}",
                    f"{stats['output_tokens']:,}",
                    f"{stats['total_tokens']:,}",
                    f"${stats['cost']:.4f}"
                )

            self.console.print(provider_table)

        # Operation breakdown
        if summary['by_operation']:
            operation_table = Table(title="🎯 Usage by Operation")
            operation_table.add_column("Operation", style="cyan")
            operation_table.add_column("Calls", style="yellow")
            operation_table.add_column("Input", style="blue")
            operation_table.add_column("Output", style="green")
            operation_table.add_column("Total", style="magenta")
            operation_table.add_column("Cost", style="red")

            # Sort by total tokens descending
            sorted_operations = sorted(
                summary['by_operation'].items(),
                key=lambda x: x[1]['total_tokens'],
                reverse=True
            )

            for operation, stats in sorted_operations:
                operation_table.add_row(
                    operation.replace('_', ' ').title(),
                    str(stats['calls']),
                    f"{stats['input_tokens']:,}",
                    f"{stats['output_tokens']:,}",
                    f"{stats['total_tokens']:,}",
                    f"${stats['cost']:.4f}"
                )

            self.console.print(operation_table)

        # Cost breakdown if there are costs
        if summary['total_cost'] > 0:
            cost_info = f"""
💰 **Cost Breakdown:**
• Total estimated cost: ${summary['total_cost']:.4f}
• Average cost per call: ${summary['total_cost'] / summary['total_calls']:.4f}
• Cost per 1K tokens: ${(summary['total_cost'] * 1000) / summary['total_tokens']:.4f}

*Note: Costs are estimates based on current public pricing and may not reflect actual billing.*
            """
            self.console.print(Panel(cost_info.strip(), title="💰 Cost Analysis", border_style="yellow"))


# Global token tracker instance
token_tracker = TokenTracker()
