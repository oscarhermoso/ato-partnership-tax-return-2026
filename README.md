# Fillable ATO Partnership tax return 2026

The ATO publishes the [Partnership tax return 2026](https://www.ato.gov.au/forms-and-instructions/partnership-tax-return-2026-instructions) (NAT 0659) as a print-only PDF, so every box has to be filled in by hand.

[`ex_0659-6.2026-fillable.pdf`](ex_0659-6.2026-fillable.pdf) is the same form with 841 fillable fields laid over the printed boxes. You can type into it in any PDF viewer and then print it.

> [!WARNING]
> **The ATO asks for this form to be completed by hand.** Its own instructions say to print clearly using a black pen only, in BLOCK LETTERS, one character per box. The ATO hasn't approved typed or printed entries, so it may not accept or correctly process a return filled in with this PDF. Use it at your own risk, for example to draft your answers before copying them onto the official form by hand. You can also lodge online through ATO Online services for business or a registered tax agent.

## What's in the form

- **Character boxes** (names, addresses, TFN, ABN, dates): each row of boxes is one field that puts one character in each box and stops when the row is full.
- **Amounts split by printed commas:** each group of digits is its own field, filled from the right. To enter $1,234,567, type `1`, Tab, `234`, Tab, `567`.
- **Wide amount boxes** (item 5, items 39–48): one right-aligned field each.
- **Tick boxes:** Yes/No, Title and status labels (B1–B3, Z2, G1/G2, E1–E3).
- **One-box codes:** a one-character text field, such as the `L` box for a loss or a CODE box.
- **Signature boxes:** plain text fields. You still sign the printed copy by hand.

The "SMITH ST" example boxes and the "Office use only" area have no fields.

## Things to know

- Each "Partnership TFN" at the top of pages 3, 5, 7 and 9 is a separate field, so type the TFN on each page.
- Whether a short amount sits on the right of its boxes depends on your PDF viewer. It works in Acrobat and most browsers, but check before printing.
- Use the official [instructions](https://www.ato.gov.au/forms-and-instructions/partnership-tax-return-2026-instructions) to work out what goes where. This repo only makes the form typeable and gives no tax advice.

## Regenerating the form

`make_fillable.py` finds the printed boxes in the original ATO form, [`ex_0659-6.2026.pdf`](ex_0659-6.2026.pdf) (included in this repo), and adds a field over each one.

```sh
pip install -r requirements.txt
python3 make_fillable.py            # writes ex_0659-6.2026-fillable.pdf
python3 make_fillable.py --dump     # lists tick boxes and single-box fields, to review
```

The detection is tuned to this form's layout: box sizes, gaps between boxes, and the labels next to tick boxes. It may need adjusting for other ATO forms.

## Copyright and disclaimer

The Partnership tax return 2026 form is © Australian Taxation Office for the Commonwealth of Australia. The ATO's [copyright notice](https://www.ato.gov.au/about-ato/using-our-website/copyright-notice) allows its material to be copied, adapted, modified, transmitted and distributed, as long as this isn't done in a way that suggests the ATO or the Commonwealth endorses you or your services or products.

This project adapts that form by adding fillable fields. It isn't affiliated with, endorsed by or approved by the ATO or the Commonwealth of Australia. It's provided as is, with no warranty. It isn't tax advice, and you're responsible for the accuracy of anything you lodge.
