# rimworld_friends

Simple utility script for parsing the Facebook friend list for Rimworld.

Based on CSVNameBank by erdelf.

# Usage

1. Obtain your Facebook profile data: https://www.facebook.com/help/131112897028467
2. Extract it in this folder.
3. Install the required Python3 packages (`bs4`, `dateutil`, and `requests`). Recommend using virtualenv for this.
4. Register on https://gender-api.com/en/ to obtain the API key if you want to automatically deduce gender from names.
5. Modify script.py as desired (e.g. set `GET_GENDER` and `GENDER_API_KEY`) and run it.
6. Verify that the output (NameDatabase.csv) is correct and modify manually as desired.
7. Copy the file NameDatabase.csv to `../mod/FriendNameBank` and overwrite the existing file.
8. Copy the entire mod to your RimWorld mod folder.
9. Make friendly hats
