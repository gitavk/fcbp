# -*- coding: utf-8 -*-
from rest_framework import routers

from .views import (
    Sales, Visits, Birthdays, ActiveClubCard, CreditsClubCard, NewUid,
    CommonList, FullList, RepFitnessClubCard, RepPersonalClubCard,
    RepIntroductory, TotalClubCard, TotalActiveClubCard, RepDiscount,
    CardDisabled, CardProspect, BestLoyalty, PeriodSales,
    ExtrProlongation, VisitsPeriod, OtherPayments, Freeze, ActivePersonal,
    UsePersonals, TotalPersonals, RUPC)


router = routers.SimpleRouter()
router.register(r'sales', Sales,  base_name='sales')
router.register(r'visits', Visits,  base_name='visits')
router.register(r'birthdays', Birthdays,  base_name='birthdays')
router.register(r'acc', ActiveClubCard,  base_name='acc')
router.register(r'ccc', CreditsClubCard,  base_name='ccc')
router.register(r'new_uid', NewUid,  base_name='new_uid')
router.register(r'cl', CommonList,  base_name='cl')
router.register(r'fl', FullList,  base_name='fl')
router.register(r'fcc', RepFitnessClubCard,  base_name='fcc')
router.register(r'tcc', RepPersonalClubCard,  base_name='tcc')
router.register(r'icc', RepIntroductory,  base_name='icc')
router.register(r'totalcc', TotalClubCard,  base_name='totalcc')
router.register(r'totalacc', TotalActiveClubCard,  base_name='totalacc')
router.register(r'ccdiscounts', RepDiscount,  base_name='ccdiscounts')
router.register(r'ccdisabled', CardDisabled,  base_name='ccdisabled')
router.register(r'ccprospect', CardProspect,  base_name='ccprospect')
router.register(r'bl', BestLoyalty,  base_name='bl')
router.register(r'ps', PeriodSales,  base_name='ps')
router.register(r'ep', ExtrProlongation,  base_name='ep')
router.register(r'visits_p', VisitsPeriod,  base_name='visits_p')
router.register(r'op', OtherPayments,  base_name='op')
router.register(r'freeze', Freeze,  base_name='freeze')

router.register(r'apc', ActivePersonal,  base_name='apc')
router.register(r'upc', UsePersonals,  base_name='upc')
router.register(r'tpc', TotalPersonals,  base_name='tpc')
router.register(r'rupc', RUPC,  base_name='rupc')

urlpatterns = router.urls
