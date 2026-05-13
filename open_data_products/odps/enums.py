# Copyright 2024 ODPS Python Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Enumeration classes for ODPS v4.1 constants
"""

from enum import Enum


class ProductStatus(Enum):
    """Valid product status values according to ODPS v4.0"""

    ANNOUNCEMENT = "announcement"
    DRAFT = "draft"
    DEVELOPMENT = "development"
    TESTING = "testing"
    ACCEPTANCE = "acceptance"
    PRODUCTION = "production"
    SUNSET = "sunset"
    RETIRED = "retired"

    @classmethod
    def values(cls):
        """Return list of all valid status values"""
        return [item.value for item in cls]


class ProductVisibility(Enum):
    """Valid product visibility values according to ODPS v4.0"""

    PRIVATE = "private"
    INVITATION = "invitation"
    ORGANISATION = "organisation"
    DATASPACE = "dataspace"
    PUBLIC = "public"

    @classmethod
    def values(cls):
        """Return list of all valid visibility values"""
        return [item.value for item in cls]


class ProductType(Enum):
    """Common product type values according to ODPS v4.0"""

    RAW_DATA = "raw data"
    DERIVED_DATA = "derived data"
    DATASET = "dataset"
    REPORTS = "reports"
    ANALYTIC_VIEW = "analytic view"
    VISUALIZATION_3D = "3D visualisation"
    ALGORITHM = "algorithm"
    DECISION_SUPPORT = "decision support"
    AUTOMATED_DECISION_MAKING = "automated decision-making"
    DATA_ENHANCED_PRODUCT = "data-enhanced product"
    DATA_DRIVEN_SERVICE = "data-driven service"
    DATA_ENABLED_PERFORMANCE = "data-enabled performance"
    BI_DIRECTIONAL = "bi-directional"

    @classmethod
    def values(cls):
        """Return list of all valid type values"""
        return [item.value for item in cls]


class DataContractType(Enum):
    """Valid data contract type values"""

    ODCS = "ODCS"  # Open Data Contract Standard
    DCS = "DCS"  # Data Contract Specification

    @classmethod
    def values(cls):
        """Return list of all valid contract type values"""
        return [item.value for item in cls]


class OutputPortType(Enum):
    """Common output port type values for data access"""

    FILE = "file"
    API = "API"
    DATABASE = "database"
    STREAM = "stream"
    WEBHOOK = "webhook"
    AI = "AI"  # New in v4.1 - AI agent integration via MCP

    @classmethod
    def values(cls):
        """Return list of all valid output port type values"""
        return [item.value for item in cls]


class AuthenticationMethod(Enum):
    """Common authentication method values"""

    NONE = "none"
    API_KEY = "api-key"
    BEARER_TOKEN = "bearer-token"
    BASIC_AUTH = "basic-auth"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"
    CUSTOM = "custom"

    @classmethod
    def values(cls):
        """Return list of all valid authentication method values"""
        return [item.value for item in cls]


class DataFormat(Enum):
    """Common data format values"""

    JSON = "JSON"
    CSV = "CSV"
    XML = "XML"
    PARQUET = "parquet"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    YAML = "YAML"
    EXCEL = "excel"
    PDF = "PDF"

    @classmethod
    def values(cls):
        """Return list of all valid format values"""
        return [item.value for item in cls]


class SLADimensionType(Enum):
    """Standardized SLA dimension types according to ODPS v4.0"""

    LATENCY = "latency"
    UPTIME = "uptime"
    RESPONSE_TIME = "responseTime"
    ERROR_RATE = "errorRate"
    END_OF_SUPPORT = "endOfSupport"
    END_OF_LIFE = "endOfLife"
    UPDATE_FREQUENCY = "updateFrequency"
    TIME_TO_DETECT = "timeToDetect"
    TIME_TO_NOTIFY = "timeToNotify"
    TIME_TO_REPAIR = "timeToRepair"
    EMAIL_RESPONSE_TIME = "emailResponseTime"

    @classmethod
    def values(cls):
        """Return list of all valid SLA dimension types"""
        return [item.value for item in cls]


class DataQualityDimensionType(Enum):
    """Standardized data quality dimension types according to ODPS v4.0"""

    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONFORMITY = "conformity"
    CONSISTENCY = "consistency"
    COVERAGE = "coverage"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"

    @classmethod
    def values(cls):
        """Return list of all valid data quality dimension types"""
        return [item.value for item in cls]


class PricingModel(Enum):
    """Standardized pricing models according to ODPS v4.0"""

    RECURRING = "recurring time period based"
    ONE_TIME = "one-time payments"
    PAY_AS_YOU_GO = "pay-as-you-go"
    REVENUE_SHARING = "revenue sharing"
    DATA_VOLUME = "data volume plan"
    TRIAL = "trial"
    DYNAMIC = "dynamic pricing"
    PAY_WHAT_YOU_WANT = "pay what you want"
    FREEMIUM = "freemium"
    OPEN_DATA = "open data"
    VALUE_BASED = "value-based"
    ON_REQUEST = "on request"

    @classmethod
    def values(cls):
        """Return list of all valid pricing model values"""
        return [item.value for item in cls]


class KPIDirection(Enum):
    """KPI target direction values according to ODPS v4.1"""

    INCREASE = "increase"
    DECREASE = "decrease"
    AT_LEAST = "at_least"
    AT_MOST = "at_most"
    EQUALS = "equals"

    @classmethod
    def values(cls):
        """Return list of all valid KPI direction values"""
        return [item.value for item in cls]


class KPIUnit(Enum):
    """Common KPI measurement units according to ODPS v4.1"""

    PERCENTAGE = "percentage"
    MINUTES = "minutes"
    SECONDS = "seconds"
    HOURS = "hours"
    DAYS = "days"
    COUNT = "count"
    CURRENCY = "currency"
    RATIO = "ratio"
    SCORE = "score"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    GIGABYTES = "gigabytes"
    TERABYTES = "terabytes"
    REQUESTS = "requests"
    TRANSACTIONS = "transactions"
    USERS = "users"
    ERRORS = "errors"
    RECORDS = "records"

    @classmethod
    def values(cls):
        """Return list of all valid KPI unit values"""
        return [item.value for item in cls]
