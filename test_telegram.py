from notifiers.telegram_sender import send_telegram_message


def main():
    result = send_telegram_message(
        "Crypto Research Agent Telegram test message"
    )

    print(result)


if __name__ == "__main__":
    main()