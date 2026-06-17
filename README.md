## Sample Raw Data Description

```plaintext
                                                   +----------------------+      +----------------------+       +----------------------+    
                    +----------------------+       |  raw_form_submission |      |     raw_email        |       |    raw_event_        |
                    |    raw_web_page_     |       |         _events      |      |   _engagement_events |       |   interaction_events |
                    |    view_events       |       |----------------------|      |----------------------|       |----------------------|
                    |----------------------|       | event_id             |      | event_id             |       | event_id             |
                    | event_id             |       | event_ts             |      | event_ts             |       | event_ts             |
                    | event_ts             |       | form_id              |      | campaign_id          |       | event_name           |
                    | session_id           |       | contact_email        |      | contact_id           |       | interaction_type     |
                    | cookie_id            |       | contact_first_name   |      | email_address        |       | badge_id             |
                    | contact_id           |       | contact_last_name    |      | event_type           |       | contact_id           |
                    | page_url             |       | company_name         |      | message_id           |       | exhibition_id        |
                    | page_type            |       | country              |      | campaign_name        |       | booth_id             |
                    | market               |       | interest_type        |      | market               |       | session_id           |
                    | device_type          |       | event_name           |      |                      |       | speaker_id           |
                    | referrer             |       | source_Channel       |      |                      |       | scan_source          |
                    |                      |       |                      |      |                      |       |                      |
                    +----------------------+       +----------------------+      +----------------------+       +----------------------+
                           |                                |                            |                               |
                           |                                |                            |                               |
                           |──────────────────────────────────────────────────────────────────────────────────────────────|
                                             |                                                 |                        |
                                             |                                                 |                        |
                                             |                                   +----------------------+       +----------------------+
                                             |                                   | raw_crm_contract_    |       |  raw_sales_activity_ |
                                             |                                   | events               |       |  events              |
                                             |                                   |----------------------|       |----------------------|
                                             |                                   | event_id             |       | event_id             |
                                             |                                   | event_ts             |       | event_ts             |
                                             |                                   | contact_id           |       | activity_type        |
                               ┌────────────────────────┐                        | account_id           |       | contact_id           |
                               |        Stream          |                        | lifecycle_stage      |       | account_id           |
                               |      Processing        |                        | lead_status          |       | sales_rep_id         |
                               |        Engine          |                        | owner_user_id        |       | next_step            |
                               └────────────────────────┘                        | last_activity_ts     |       | outcome              |
                                                                                 | source_system        |       | due_date             |
                                                                                 | change_type          |       |                      |
                                                                                 |                      |       |                      |
                                                                                 +----------------------+       +----------------------+ 
```

* raw_web_page_view_events - Tracks Website Behaviour
    * homepage visit
    * exhibitor directory view  
    * ticket page visit
    * booth inquiry page visit

* raw_form_submission_events - Tracks lead capture and inbound interest.
    * download exhibitor list
    * request callback  
    * event brochure download
    * contact us submission

* raw_email_engagement_events - Tracks nurture and campaign interaction.
    * sent
    * delivered
    * opened
    * clicked
    * unsubscribed

* raw_event_interaction_events - Tracks offline / event-side behavior.
    * badge scan at booth
    * seminar attendanc
    * meeting booked onsite
    * lead captured by staff

* raw_crm_contact_events - Tracks changes coming from SAP Sales Cloud V2 or marketing CRM.
    * Lnew contact created
    * Plead qualified
    * Blead rejected
    * Bopportunity created
    * owner changed

* raw_sales_activity_events - Tracks sales actions.
    * call completed
    * meeting scheduled
    * quote requested
    * follow-up sent



                    