# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/50_activity_log.ipynb.

# %% auto 0
__all__ = ['get_activity_log_object_types', 'search_activity_log']

# %% ../../nbs/routes/50_activity_log.ipynb 3
import aiohttp

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.DomoAuth as dmda


# %% ../../nbs/routes/50_activity_log.ipynb 4
async def get_activity_log_object_types(auth: dmda.DomoAuth) -> rgd.ResponseGetData:
    """retrieves a list of valid objectTypes that can be used to search the activity_log API"""

    url = "https://domo-dojo.domo.com/api/audit/v1/user-audits/objectTypes"

    return await gd.get_data(url=url, method="GET", auth=auth)

# %% ../../nbs/routes/50_activity_log.ipynb 7
async def search_activity_log(
    auth: dmda.DomoAuth,
    start_time: int,  # epoch time in milliseconds
    end_time: int,  # epoch time in milliseconds
    maximum: int,
    object_type: str = None,
    session: aiohttp.ClientSession = None,
    debug_api: bool = False,
    debug_loop: bool = False,
) -> rgd.ResponseGetData:
    """loops over activity log api to retrieve audit logs"""

    is_close_session = False

    if not session:
        session = aiohttp.ClientSession()
        is_close_session = True

    url = f"https://{auth.domo_instance}.domo.com/api/audit/v1/user-audits"

    if object_type and object_type != 'ACTIVITY_LOG':
        url = f"{url}/objectTypes/{object_type}"

    fixed_params = {"end": end_time, "start": start_time}

    offset_params = {
        "offset": "offset",
        "limit": "limit",
    }

    def arr_fn(res) -> list[dict]:
        return res.response

    res = await gd.looper(
        auth=auth,
        method="GET",
        url=url,
        arr_fn=arr_fn,
        fixed_params=fixed_params,
        offset_params=offset_params,
        session=session,
        maximum=maximum,
        debug_loop=debug_loop,
        debug_api=debug_api,
    )

    if is_close_session:
        await session.close()

    return res

