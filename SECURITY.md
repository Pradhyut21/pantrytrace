# Security and responsible use

This is a local research prototype with synthetic data, not production inventory software.

Never commit credentials, recipient details, real beneficiary data, or private pantry exports. `.env` files and local H-MEM state are ignored. Use environment variables for sponsor access and a least-privilege read-only Zetaris account.

Run the workbench on loopback only. No external communication or inventory action is executed. Evidence exports may contain whatever operational information you supply in future connected use; review them before sharing.

For a security concern, open a minimal issue without secrets or sensitive data, then arrange a private channel with the repository owner. Do not paste live records or API keys into issues.
