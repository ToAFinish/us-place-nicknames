# Contribute to US Place Nicknames

Thank you for your help. You can add a nickname, correct an error, or add a source.

## Method 1: Use an issue form (no Git knowledge necessary)

1. Go to the [Issues](../../issues/new/choose) tab.
2. Select **Add a nickname** or **Report an error**.
3. Fill in the form. Then click **Submit**.

A maintainer examines the issue and changes the data.

## Method 2: Edit the data and open a pull request

1. Open the applicable file in the `data/` folder.
2. Click the pencil icon to edit the file. GitHub makes a copy (fork) for you.
3. Add one row for each nickname. Use the column order in the first row.
4. Click **Commit changes**. Then click **Create pull request**.

An automatic check runs on the pull request. If the check finds an error, it shows the line and the problem.

### Edit on your computer

```bash
git clone https://github.com/ToAFinish/us-place-nicknames.git
cd us-place-nicknames
# Edit data/*.csv
python scripts/validate.py --fix   # sorts rows and removes extra spaces
python scripts/validate.py         # must show 0 errors
```

The scripts need Python 3.8 or later. They do not need other packages.

## Rules for the data

- **One nickname on each row.** Do not put ";" between nicknames.
- **Keep the original words and capitals.** Write the nickname as the source writes it.
- **Use the two-letter USPS state code** in the `state` column, for example `TX`.
- **Counties:** Do not write "County" or "Parish" in the `county` column. Put the type in `county_type`.
  If you know the five-digit FIPS code, put it in `county_fips`.
- **Give a source** when possible: a URL, or a book title with the page number.
- **Put quotes around a value that contains a comma**, for example `"The City Built on Oil, Soil and Toil"`.
  A spreadsheet program does this automatically when it saves a CSV file.
- **Do not add duplicates.** The check finds a nickname that is already in the file for the same place.
- **Do not add insults or hate speech.** A maintainer removes them.

## Spreadsheet programs

You can edit the files in Excel, Google Sheets, or LibreOffice. Obey these rules:

- Save as **CSV UTF-8**.
- Do not let the program change FIPS codes. For example, `01049` must not become `1049`.
  Set the `county_fips` column to the **Text** format.
- After you save, run `python scripts/validate.py --fix` to put the rows in the correct order.

## Releases (for maintainers)

1. Make sure that `python scripts/validate.py` shows 0 errors.
2. Make a tag, for example `git tag v1.1.0` and `git push origin v1.1.0`.
3. The release workflow makes the download files and attaches them to a new release.
