from fastapi import HTTPException
from api.schemas import FinancialRecord

def parse_income_command(args: list) -> FinancialRecord:
    try:
        if len(args) < 2:
            raise ValueError("Format: `/add_income [amount] [currency] [category]`")
            
        return FinancialRecord(
            amount=float(args[0]),
            currency_code=args[1].upper(),
            category_name=" ".join(args[2:]) if len(args) > 2 else "General",
            description=f"Income: {' '.join(args[2:])}" if len(args) > 2 else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def parse_expense_command(args: list) -> FinancialRecord:
    try:
        if len(args) < 2:
            raise ValueError("Format: `/add_expense [amount] [currency] [category]`")
            
        return FinancialRecord(
            amount=float(args[0]),
            currency_code=args[1].upper(),
            category_name=" ".join(args[2:]) if len(args) > 2 else "General",
            description=f"Expense: {' '.join(args[2:])}" if len(args) > 2 else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))