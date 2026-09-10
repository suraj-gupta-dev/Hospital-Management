import random
import string
from django.utils import timezone



def generate_employee_id_with_hospital_code(h_code="HOS"):
    """
    Generate employee ID with company code and year
    Example: ABC-2026-12345
    """
    uppercase = string.ascii_uppercase()
    digits = string.digits()
    
     

