# app/repositories/common.py
def dept_filter_clause(dept_id: int | None, table_alias: str = "") -> str:
    """
    dept_id None ise (ADMIN) filtre yok, değilse 'AND <alias>department_id = %s' döner.
    table_alias: 'c.' gibi kullanılabilir.
    """
    prefix = f"{table_alias}" if (table_alias == "" or table_alias.endswith(".")) else f"{table_alias}."
    return "" if dept_id is None else f" AND {prefix}department_id = %s "
