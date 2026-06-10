# `tap-hubspot`

tap-hubspot is a Singer tap for Hubspot.

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`
* `batch`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| access_token        | False    | None    | Token to authenticate against the API service |
| client_id           | False    | None    | The OAuth app client ID. |
| client_secret       | False    | None    | The OAuth app client secret. |
| refresh_token       | False    | None    | The OAuth app refresh token. |
| start_date          | False    | None    | Earliest record date to sync |
| end_date            | False    | None    | Latest record date to sync |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |
| batch_config        | False    | None    |             |
| custom_object_types | False    | None    | List of HubSpot custom CRM object type names to sync (e.g. `['patches']`). Requires HubSpot Enterprise and `crm.objects.custom.read` + `crm.schemas.custom.read` scopes. |

A full list of supported settings and capabilities is available by running: `tap-hubspot --about`

## Elastic License 2.0

The licensor grants you a non-exclusive, royalty-free, worldwide, non-sublicensable, non-transferable license to use, copy, distribute, make available, and prepare derivative works of the software.

## Installation

```bash
pipx install git+https://github.com/MeltanoLabs/tap-hubspot.git
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

A Hubspot access token is required to make API requests. (See [Hubspot API](https://developers.hubspot.com/docs/api/working-with-oauth) docs for more info)


### Streams

| Stream | Replication | Description |
|:-------|:-----------:|:------------|
| `contacts` | Incremental | People in your HubSpot CRM |
| `companies` | Incremental | Company records in your CRM |
| `deals` | Incremental | Sales opportunities and pipeline deals |
| `leads` | Incremental | Individual sales leads linked to a contact and company (`objectTypeId: 0-136`) |
| `line_items` | Incremental | Products attached to deals |
| `goal_targets` | Incremental | Sales and activity goal records |
| `calls` | Incremental | Call engagement records |
| `communications` | Incremental | Communication engagement records |
| `emails` | Incremental | Email engagement records |
| `meetings` | Incremental | Meeting engagement records |
| `notes` | Incremental | Note engagement records |
| `postal_mail` | Incremental | Postal mail engagement records |
| `tasks` | Incremental | Task engagement records |
| `owners` | Full Table | HubSpot users who own CRM records |
| `users` | Full Table | Users in your HubSpot account |
| `teams` | Full Table | HubSpot Teams and their member user IDs |
| `products` | Full Table | Product library items |
| `tickets` | Full Table | Customer support tickets |
| `quotes` | Full Table | Sales quotes |
| `feedback_submissions` | Full Table | Customer feedback survey responses |
| `ticket_pipelines` | Full Table | Ticket pipeline and stage definitions |
| `deal_pipelines` | Full Table | Deal pipeline and stage definitions |
| `email_subscriptions` | Full Table | Email subscription type definitions |
| `properties` | Full Table | Property definitions for all CRM object types |

### Permissions

The following scopes need to be added to your access token to access the following endpoints:

- Contacts: `crm.objects.contacts.read`
- Companies: `crm.objects.companies.read`
- Deals: `crm.objects.deals.read`
- Leads: `crm.objects.leads.read`
- Owners: `crm.objects.owners.read`
- Users: `settings.users.read`
- Teams: `settings.users.teams.read`
- Feedback Submissions: `crm.objects.feedback_submissions.read`
- Calls: `crm.objects.calls.read`
- Communications: `crm.objects.communications.read`
- Emails: `sales-email-read`
- Meetings: `crm.objects.meetings.read`
- Notes: `crm.objects.notes.read`
- Postal Mail: `crm.objects.postal_mail.read`
- Tasks: `crm.objects.tasks.read`
- Line Items: `e-commerce`
- Products: `e-commerce`
- Tickets: `tickets`
- Ticket Pipelines: `tickets`
- Deal Pipelines: `crm.objects.deals.read`
- Quotes: `crm.objects.quotes.read`
- Goal Targets: `crm.objects.goals.read`
- Email Subscriptions: `content`
- Properties: same scopes as the corresponding object type
- Custom Objects: `crm.objects.custom.read` and `crm.schemas.custom.read` (HubSpot Enterprise only)

For more info on the streams and permissions, check the [Hubspot API Documentation](https://developers.hubspot.com/docs/api/overview).

## Usage

You can easily run `tap-hubspot` by itself or in a pipeline using [Meltano](https://meltano.com/).


### Streams Using v1 Endpoints

The following Streams use the v1 (legacy) endpoint in the Hubspot API:

1. [TicketPipeline & DealPipeline](https://legacydocs.hubspot.com/docs/methods/pipelines/pipelines_overview): The v3 endpoint requires a pipeline ID parameter to make calls to the API. Because of this,
you are limited to only pulling data for a single pipeline ID from v3, whereas the v1 API allows you to pull from all pipelines.
2. [EmailSubscriptions](https://legacydocs.hubspot.com/docs/methods/email/email_subscriptions_overview): The v3 endpoint requires you to set a single email address to pull subscription data, whereas
the v1 endpoint allows you to pull data from all emails.


## Stream Inheritance

This project uses parent-child streams. Learn more about them [here](https://gitlab.com/meltano/sdk/-/blob/main/docs/parent_streams.md).

### Executing the Tap Directly

```bash
tap-hubspot --version
tap-hubspot --help
tap-hubspot --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # https://docs.astral.sh/uv/getting-started/installation/
uv sync
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
uv run pytest
```

You can also test the `tap-hubspot` CLI interface directly using `uv run`:

```bash
uv run tap-hubspot --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
uv tool install meltano
# Initialize meltano within this directory
cd tap-hubspot
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-hubspot --version
# OR run a test EL pipeline:
meltano run tap-hubspot target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
