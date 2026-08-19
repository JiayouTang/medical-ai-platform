from dataclasses import dataclass
from typing import Any

from sqlalchemy import DECIMAL, Column, Integer, MetaData, Table, Text
from sqlalchemy.sql.type_api import TypeEngine


STRING_OPS = ("=", "!=", "in", "not_in", "like", "is_null", "is_not_null")
NUMERIC_OPS = (
    "=",
    "!=",
    ">",
    ">=",
    "<",
    "<=",
    "in",
    "not_in",
    "between",
    "is_null",
    "is_not_null",
)


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    data_type: str
    description: str
    allowed_ops: tuple[str, ...]
    numeric: bool = False


@dataclass(frozen=True)
class TableSpec:
    name: str
    description: str
    columns: dict[str, ColumnSpec]


INPATIENT_COLUMNS: dict[str, ColumnSpec] = {
    "HospitalServiceArea": ColumnSpec("HospitalServiceArea", "string", "Hospital service area.", STRING_OPS),
    "HospitalCounty": ColumnSpec("HospitalCounty", "string", "Hospital county.", STRING_OPS),
    "OperatingCertificateNumber": ColumnSpec(
        "OperatingCertificateNumber", "string", "Operating certificate number.", STRING_OPS
    ),
    "PermanentFacilityId": ColumnSpec("PermanentFacilityId", "string", "Permanent facility identifier.", STRING_OPS),
    "FacilityName": ColumnSpec("FacilityName", "string", "Hospital or facility name.", STRING_OPS),
    "AgeGroup": ColumnSpec("AgeGroup", "string", "Patient age group bucket.", STRING_OPS),
    "ZipCode3Digits": ColumnSpec("ZipCode3Digits", "string", "Patient ZIP code prefix.", STRING_OPS),
    "Gender": ColumnSpec("Gender", "string", "Patient gender category.", STRING_OPS),
    "Race": ColumnSpec("Race", "string", "Patient race category.", STRING_OPS),
    "Ethnicity": ColumnSpec("Ethnicity", "string", "Patient ethnicity category.", STRING_OPS),
    "RaceEthnicity": ColumnSpec("RaceEthnicity", "string", "Race or ethnicity category.", STRING_OPS),
    "LengthOfStay": ColumnSpec("LengthOfStay", "integer", "Inpatient length of stay in days.", NUMERIC_OPS, True),
    "AdmissionType": ColumnSpec("AdmissionType", "string", "Admission type.", STRING_OPS),
    "PatientDisposition": ColumnSpec("PatientDisposition", "string", "Patient discharge disposition.", STRING_OPS),
    "DischargeYear": ColumnSpec("DischargeYear", "integer", "Hospital discharge year.", NUMERIC_OPS, True),
    "CCSRDiagnosisCode": ColumnSpec("CCSRDiagnosisCode", "string", "CCSR diagnosis code.", STRING_OPS),
    "CCSRDiagnosisDescription": ColumnSpec(
        "CCSRDiagnosisDescription", "string", "CCSR diagnosis description.", STRING_OPS
    ),
    "CCSRProcedureCode": ColumnSpec("CCSRProcedureCode", "string", "CCSR procedure code.", STRING_OPS),
    "CCSRProcedureDescription": ColumnSpec(
        "CCSRProcedureDescription", "string", "CCSR procedure description.", STRING_OPS
    ),
    "APRDRGCode": ColumnSpec("APRDRGCode", "integer", "APR DRG code.", NUMERIC_OPS, True),
    "APRDRGDescription": ColumnSpec("APRDRGDescription", "string", "APR DRG description.", STRING_OPS),
    "APRMDCCode": ColumnSpec("APRMDCCode", "integer", "APR MDC code.", NUMERIC_OPS, True),
    "APRMDCDescription": ColumnSpec("APRMDCDescription", "string", "APR MDC description.", STRING_OPS),
    "APRSeverityOfIllnessCode": ColumnSpec(
        "APRSeverityOfIllnessCode", "integer", "APR severity of illness code.", NUMERIC_OPS, True
    ),
    "APRSeverityOfIllnessDescription": ColumnSpec(
        "APRSeverityOfIllnessDescription", "string", "APR severity of illness description.", STRING_OPS
    ),
    "APRRiskOfMortality": ColumnSpec("APRRiskOfMortality", "string", "APR risk of mortality category.", STRING_OPS),
    "APRMedicalSurgicalDescription": ColumnSpec(
        "APRMedicalSurgicalDescription", "string", "APR medical/surgical category.", STRING_OPS
    ),
    "PaymentTypology1": ColumnSpec("PaymentTypology1", "string", "Primary payment typology.", STRING_OPS),
    "PaymentTypology2": ColumnSpec("PaymentTypology2", "string", "Secondary payment typology.", STRING_OPS),
    "PaymentTypology3": ColumnSpec("PaymentTypology3", "string", "Tertiary payment typology.", STRING_OPS),
    "BirthWeight": ColumnSpec("BirthWeight", "integer", "Birth weight in grams for newborn records.", NUMERIC_OPS, True),
    "EmergencyDepartmentIndicator": ColumnSpec(
        "EmergencyDepartmentIndicator", "string", "Emergency department indicator.", STRING_OPS
    ),
    "TotalCharges": ColumnSpec("TotalCharges", "decimal", "Total hospital charges.", NUMERIC_OPS, True),
    "TotalCosts": ColumnSpec("TotalCosts", "decimal", "Total hospital costs.", NUMERIC_OPS, True),
}


TABLES: dict[str, TableSpec] = {
    "inpatient": TableSpec(
        name="inpatient",
        description=(
            "Hospital inpatient discharge records. Development data can be synthetic sample rows or cleaned "
            "SPARCS 2021 rows loaded through scripts/load_sparcs_mysql.py."
        ),
        columns=INPATIENT_COLUMNS,
    )
}


def get_table_spec(table_name: str) -> TableSpec:
    try:
        return TABLES[table_name]
    except KeyError as exc:
        allowed = ", ".join(sorted(TABLES))
        raise KeyError(f"Unknown table {table_name!r}. Allowed tables: {allowed}") from exc


def get_column_spec(table_name: str, column_name: str) -> ColumnSpec:
    table = get_table_spec(table_name)
    try:
        return table.columns[column_name]
    except KeyError as exc:
        allowed = ", ".join(sorted(table.columns))
        raise KeyError(f"Unknown field {column_name!r} for table {table_name!r}. Allowed fields: {allowed}") from exc


def table_names() -> list[str]:
    return sorted(TABLES)


def column_names(table_name: str) -> list[str]:
    return list(get_table_spec(table_name).columns)


def sqlalchemy_type(data_type: str) -> TypeEngine[Any]:
    if data_type == "integer":
        return Integer()
    if data_type == "decimal":
        return DECIMAL(14, 2)
    return Text()


def build_sqlalchemy_table(table_name: str, metadata: MetaData | None = None) -> Table:
    table_spec = get_table_spec(table_name)
    metadata = metadata or MetaData()
    return Table(
        table_spec.name,
        metadata,
        *(Column(column.name, sqlalchemy_type(column.data_type)) for column in table_spec.columns.values()),
    )


def public_schema() -> dict[str, Any]:
    return {
        "tables": [
            {
                "name": table.name,
                "description": table.description,
                "columns": [
                    {
                        "name": column.name,
                        "type": column.data_type,
                        "description": column.description,
                        "allowed_operations": list(column.allowed_ops),
                        "numeric": column.numeric,
                    }
                    for column in table.columns.values()
                ],
            }
            for table in TABLES.values()
        ]
    }
