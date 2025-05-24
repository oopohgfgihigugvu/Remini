from os import getenv
from dotenv import load_dotenv
load_dotenv()
class Config:
    API_ID = int(getenv("API_ID", "16457832"))
    API_HASH = getenv("API_HASH", "3030874d0befdb5d05597deacc3e83ab")
    BOT_TOKEN = getenv("BOT_TOKEN", "7576739341:AAGD9WIAt9lI_Tw1ACiJrkRe6co66TQdNS4")
    
