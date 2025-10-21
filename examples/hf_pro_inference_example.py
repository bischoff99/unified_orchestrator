"""Example: HuggingFace Pro inference with cost monitoring and safety checks.

Demonstrates production-ready HF Pro usage with integrated MCP tools.
"""
import logging
from src.utils import HFProClient, HFCostMonitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run HF Pro inference example with cost monitoring."""
    
    print("="*60)
    print("HuggingFace Pro Inference - Production Example")
    print("="*60)
    
    # Initialize client (uses HF_TOKEN from environment)
    model_id = "meta-llama/Llama-3.1-8B-Instruct"
    
    print(f"\n📦 Initializing HF Pro client...")
    print(f"   Model: {model_id}")
    print(f"   Cost tracking: Enabled")
    print(f"   Safety checks: Enabled")
    
    client = HFProClient(
        model_id=model_id,
        enable_cost_tracking=True,
        enable_safety_checks=True,
    )
    
    # Check budget before usage
    print(f"\n💰 Checking budget status...")
    budget_status = client.check_budget()
    
    if budget_status["status"] == "EXCEEDED":
        print(f"   ❌ Budget exceeded! Cannot use HF Pro")
        print(f"   💡 Recommendation: Use Ollama backend instead")
        return
    
    print(f"   Status: {budget_status['status']}")
    print(f"   Daily budget: £{budget_status['budget']:.2f}")
    print(f"   Spent: £{budget_status['spent']:.2f} ({budget_status['percentage']:.1f}%)")
    print(f"   Remaining: £{budget_status['remaining']:.2f}")
    
    # Estimate cost for planned generation
    print(f"\n📊 Estimating cost for 100 tokens...")
    estimate = client.estimate_cost(tokens=100)
    print(f"   Cost: £{estimate['total_cost_gbp']:.4f}")
    print(f"   Daily budget impact: {estimate['daily_budget_pct']:.2f}%")
    
    # Example 1: Simple generation
    print(f"\n🚀 Example 1: Simple text generation")
    prompt = "Explain quantum computing in simple terms:"
    
    print(f"   Prompt: {prompt}")
    print(f"   Generating...")
    
    result = client.generate(
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        check_budget=True,
        validate_safety=True,
    )
    
    if result["status"] == "success":
        print(f"\n✅ Generation successful!")
        print(f"   Latency: {result['latency_ms']:.1f}ms")
        print(f"   Tokens used: {result['tokens_used']}")
        print(f"   Generated text:")
        print(f"   {result['text'][:200]}...")
        
        # Safety check results
        if result.get("safety_check"):
            safety = result["safety_check"]
            safety_status = "✅ PASSED" if safety["passed"] else "⚠️ FAILED"
            print(f"\n🛡️  Safety validation: {safety_status}")
            if not safety["passed"]:
                print(f"   Issues: {safety['issues']}")
    else:
        print(f"\n❌ Generation failed: {result.get('error')}")
    
    # Example 2: Chat format
    print(f"\n🚀 Example 2: Chat completion")
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What are the benefits of using LoRA for fine-tuning?"},
    ]
    
    print(f"   Messages: {len(messages)}")
    print(f"   Generating...")
    
    chat_result = client.chat(
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    
    if chat_result["status"] == "success":
        print(f"\n✅ Chat completion successful!")
        print(f"   Latency: {chat_result['latency_ms']:.1f}ms")
        print(f"   Tokens used: {chat_result['tokens_used']}")
        print(f"   Response:")
        print(f"   {chat_result['text'][:200]}...")
    
    # Final budget check
    print(f"\n💰 Final budget status:")
    final_budget = client.check_budget()
    print(f"   Status: {final_budget['status']}")
    print(f"   Total spent today: £{final_budget['spent']:.2f}")
    print(f"   Total requests: {final_budget['stats']['total_requests']}")
    print(f"   Total tokens: {final_budget['stats']['total_tokens']:,}")
    
    # Cost monitor summary
    print(f"\n📈 Detailed cost report:")
    monitor = HFCostMonitor()
    print(monitor.get_summary_report())
    
    print("\n" + "="*60)
    print("Example complete!")
    print("="*60)


if __name__ == "__main__":
    main()

