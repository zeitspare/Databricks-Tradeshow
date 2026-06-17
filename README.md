## High Level Architecture

```plaintext

```

## Sample Raw Data Description

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
                           |─────────────────────────────────────────────────────────────────────────────────────────────|
                                             |                                                 |                         |
                                             |                                                 |                         |
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
                                            |                                    | source_system        |       | due_date             |
                                            |                                    | change_type          |       |                      |
                                            |                                    |                      |       |                      |
                                            |                                    +----------------------+       +----------------------+ 
                                             
                               ┌────────────────────────┐
                               |     AZURE              |
                               |       DATA LAKE        |
                               └────────────────────────┘

```

## Sample Star schema Data Model (Analytics Purposes)

### Dimension Tables

* dim_contact - Unified Person Record (exhibitor_contact, private_visitor, professional_visitor, media_contact, partner_contacct)
* dim_company - Unified Company Record
* dim_exhibition - Master data for each trade show
* dim_campaign - MAster data for Campaign
* dim_channel - Report accross different channels (web, email, social, sales, onsite, partner)
* bridge_contact_identity - (email, cookie, badge_id, mobile, CRM_contact_id) for unique records.

### Fact Tables

* fact_interaction_event - One row per interaction, near real-time.(page_view, form_sumbit, email_check, booth_scan, seminar_attendance)
* fact_contact_engagement_daily - Daily rollup for behavior analytics.
* fact_lead_score_snapshot - Stores score changes over time (explaining why a lead became qualified).
* fact_lead_qualification_history - Tracks lifecycle changes (unknown, engaged, marketing qualified lead, sales accepted lead, sales rejected, lost, opputunity)
* fact_sales_handoff - Tracks transfer from marketing to sales.

```plaintext

  +----------------------+    +------------------------+    +----------------------+    +----------------------+   +----------------------+ 
  |    dim_contact       |    |  dim_company           |    |  dim_exhibition      |    |   dim_campaign       |   |   bridge_contact_    |
  |                      |    |                        |    |                      |    |                      |   |    identity          |
  |----------------------|    |------------------------|    |----------------------|    |----------------------|   |----------------------|
  | contact_key          |    | company_key            |    | exhibition_key       |    | campaign_key         |   | identity_key         |
  | source_contact_ids   |    | company_name           |    | exhibition_name      |    | campaign_name        |   | contact_key          |
  | first_name           |    | industry               |    | edition_year         |    | campaign_type        |   | identity_type        |
  | last_name            |    | size_band              |    | market               |    | channel              |   | identity_value       |
  | email                |    | country                |    | location             |    | market               |   |  match_confidence    |
  | phone                |    | city                   |    | start_date           |    | start_date           |   |  is_primary          |
  | company_key          |    | website                |    | end_date             |    | end_date             |   +----------------------+
  | country              |    | parent_company_key     |    | theme                |    |                      |     |
  |                      |    | is_exhibitor           |    | status               |    |                      |     |  
  | language             |    | is_potential_exhibito  |    |                      |    |                      |     |                             
  | persona_type         |    |                        |    |                      |    +----------------------+     |          
  | opt_in_status        |    |                        |    |                      |               |                 |    
  | created_ts           |    |                        |    +----------------------+               |                 |     +----------------------+
  | updated_ts           |    +------------------------+               |                           |                 |     |       dim_channel    |
  +----------------------+                |                            |                           |                 |     +----------------------+
           |                              |                            |                           |                 |     | channel_key          |
           |                              |                            |                           |                 |     | Channel_name         |
           |                              |                            |                           |                 |     | channel_group        |
           |                              |                            |                           |                 |     |                      |
           |                              |                            |                           |                 |     +----------------------+
           |                              |                            |                           |                 |                |                        |──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────|
                                                                | 
                                                                |  
           |──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────|
           |                              |                            |                          |                                   | 
  +----------------------+    +------------------------+    +----------------------+    +----------------------+   +----------------------+ 
  |    fact_interaction  |    |  fact_contact_         |    |  fact_lead_score_    |    |   fact_lead_         |   |   fact_sales_        |
  |       _event         |    |    engagement_daily    |    |   snapshot           |    |qualitfication_history|   |    handoff           |
  |----------------------|    |------------------------|    |----------------------|    |----------------------|   |----------------------|
  | interaction_key      |    | date_key               |    | snapshot_ts          |    | change_ts            |   | handoff_ts           |
  | event_ts             |    | contact_key            |    | contact_key          |    | contact_key          |   | contact_key          |
  | contact_key          |    | company_key            |    | behavior_score       |    | old_status           |   | account_key          |
  | company_key          |    | exhibition_key         |    | fit_score            |    | new_status           |   | assigned_sales_user  |
  | exhibition_key       |    | web_visits             |    | intent_score         |    | changed_by           |   | handoff_reason       |
  | campaign_key         |    | email_opens            |    | total_score          |    | reason               |   | trigger_rule         |
  | channel_key          |    | email_clicks           |    | qualification_status |    | rule_id              |   | sla_due_ts           |
  | interaction_type     |    | forms_submitted        |    | score_reason_code    |    |                      |   | handoff_status       |
  | interaction_value    |    | booth_scans            |    | triggered_by_event_id|    |                      |   | sales_response_ts    |
  | source_system        |    | total_engagement_score |    |                      |    |                      |   |                      |
  |                      |    |                        |    |                      |    |                      |   |                      |
  |                      |    |                        |    |                      |    |                      |   |                      |
  +----------------------+    +------------------------+    +----------------------+    +----------------------+   +----------------------+

```

                    