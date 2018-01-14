DROP VIEW v_client_online;

CREATE OR REPLACE VIEW v_client_online
AS 
(
SELECT row_number() over() as id, client_id, date, product, is_full_time
FROM (
    SELECT cc.client_id, ucc.date, 'clubcard' as product
         , pcc.is_full_time
    FROM clients_clientclubcard cc
     INNER JOIN clients_useclientclubcard ucc
        ON cc.id = ucc.client_club_card_id
     INNER JOIN products_clubcard pcc
        ON pcc.id = cc.club_card_id
     LEFT JOIN clients_useclientpersonal ucp
        ON ucc.id = ucp.club_card_visit_id
    WHERE ucc.end IS NULL AND ucp.id IS NULL

    UNION ALL

    SELECT a.client_id, ua.date, 'aqua' as product, false
    FROM v_external_aqua a
     INNER JOIN clients_useclientaquaaerobics ua
        ON a.id = ua.client_aqua_aerobics_id
    WHERE ua.end IS NULL

    UNION ALL

    SELECT t.client_id, ut.date, 'ticket' as product, false
    FROM clients_clientticket t
     INNER JOIN clients_useclientticket ut
        ON t.id = ut.client_ticket_id
    WHERE ut.end IS NULL

    UNION ALL

    SELECT p.client_id, up.date, 'personal' as product, false
    FROM clients_clientpersonal p
     INNER JOIN clients_useclientpersonal up
        ON p.id = up.client_personal_id
    WHERE up.end IS NULL
    ) online
);