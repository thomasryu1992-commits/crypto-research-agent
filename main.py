from agents.research_agent import CryptoResearchAgent


def main():
    agent = CryptoResearchAgent()
    report = agent.run_daily_research()

    print("\n" + "=" * 80)
    print("DAILY CRYPTO RESEARCH REPORT")
    print("=" * 80)
    print(report)
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
