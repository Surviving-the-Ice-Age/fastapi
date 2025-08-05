from fastapi import APIRouter, Query
from services import analysis_service as svc

router = APIRouter()

@router.get("/resident/gender-age")
def resident(trdar_cd: int):
    return svc.plot_resident_gender_age_ratio(trdar_cd)

@router.get("/workplace/gender-age")
def workplace(trdar_cd: int):
    return svc.plot_workplace_gender_age_ratio(trdar_cd)

@router.get("/floating/time")
def floating_time(trdar_cd: int):
    return svc.plot_floating_time_ratio(trdar_cd)

@router.get("/floating/age")
def floating_age(trdar_cd: int):
    return svc.plot_floating_gender_age_ratio(trdar_cd)

@router.get("/sales/gender")
def sales_gender(trdar_cd: int, induty_cd: str):
    return svc.plot_gender_sales_ratio(trdar_cd, induty_cd)

@router.get("/sales/time")
def sales_time(trdar_cd: int, induty_cd: str):
    return svc.plot_time_sales_ratio(trdar_cd, induty_cd)

@router.get("/sales/age")
def sales_age(trdar_cd: int, induty_cd: str):
    return svc.plot_age_sales_ratio(trdar_cd, induty_cd)

@router.get("/sales/monthly")
def sales_monthly(trdar_cd: int, induty_cd: str):
    return svc.plot_monthly_sales_per_store(trdar_cd, induty_cd)

@router.get("/sales/area-average")
def sales_area_avg(trdar_cd: int):
    return svc.plot_avg_sales_per_store_by_area(trdar_cd)

@router.get("/store/count")
def store_count(trdar_cd: int, induty_cd: str):
    return svc.plot_store_count_trend(trdar_cd, induty_cd)

@router.get("/store/open")
def store_open(trdar_cd: int, induty_cd: str):
    return svc.plot_open_store_trend(trdar_cd, induty_cd)

@router.get("/store/close")
def store_close(trdar_cd: int, induty_cd: str):
    return svc.plot_close_store_trend(trdar_cd, induty_cd)

@router.get("/store/franchise")
def store_franchise(trdar_cd: int, induty_cd: str):
    return svc.plot_franchise_ratio(trdar_cd, induty_cd)

@router.get("/area/summary")
def area_summary(trdar_cd: int):
    return svc.analyze_commercial_area(trdar_cd)