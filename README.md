# BigThink Article Notifier

This a very stripped down website scrapping tool, I use to stay updated on the new BigThink articles, this only works for Gmail

## How to use it
1. Install Python3 (python 3.12 preferably)
2. Create a virtual environment 
```sh
python -m venv venv
```
then activate the virtual environment, by running this 
> for unix-based systems (linux and macOS)
```sh
source activate
```
3. Install the necessary requirements with
```sh
pip install -r requirements.txt
```
4. Create a [Google App Password](https://myaccount.google.com/apppasswords)
> [!Warning]
> Ensure the email you intend to use has 2FA
> Save the password to avoid losing it
5. Create a `.env` file to keep your credentials, which are
```env
EMAIL=example@gmail.com
PASSWORD=abcd efgh ijkl mnop
```
4. Open your terminal and run
```sh
python aritcle_notifier.py <recipient_email>
```
if you want to ignore the articles from the point you ran the script run
```sh
python aritcle_notifier.py <recipient_email> --offset
```
> [!Note]
> `<recipient_email>` is a placeholder for the recipient email

## Extensibility
I tried to make it easy to add new articles to monitor

## Future Addition
I intend to keep it simple, but I will consider making it run as a daemon
