# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/client/10_get_data.ipynb.

# %% auto 0
__all__ = ['get_data', 'looper']

# %% ../../nbs/client/10_get_data.ipynb 2
from typing import Optional, Union

from pprint import pprint

import aiohttp

import domolibrary.DomoAuth as dmda
import domolibrary.client.ResponseGetData as rgd


# %% ../../nbs/client/10_get_data.ipynb 3
async def get_data(
    url: str,
    method: str,
    auth: dmda.DomoAuth,
    content_type: Optional[dict] = None,
    headers: Optional[dict] = None,
    # if no session passed by default will create and close session during execution
    session: Optional[aiohttp.ClientSession] = None,
    body: Union[dict, str, None] = None,
    params: Optional[dict] = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    """async wrapper for asyncio requests"""

    if auth and not auth.token:
        await auth.get_auth_token()

    if headers is None:
        headers = {}

    is_close_session = False
    if session is None:
        is_close_session = True
        session = session or aiohttp.ClientSession()

    headers = {
        "Content-Type": content_type or "application/json",
        "Connection": "keep-alive",
        "accept": "application/json, text/plain",
        **headers,
    }

    if auth:
        headers.update(**auth.auth_header)

    if debug_api:
        pprint(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "json": body,
                "params": params,
            }
        )

    try:
        if headers.get("Content-Type") == "application/json":
            if debug_api:
                print("passing json")

            res = await session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=body,
                params=params,
            )

        elif body is not None:
            res = await session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                data=body,
                params=params,
            )

        else:
            res = await session.request(
                method=method.upper(), url=url, headers=headers, params=params
            )

    except Exception as e:
        print(e)

    finally:
        if is_close_session:
            await session.close()

    return await rgd.ResponseGetData._from_aiohttp_response(res)

# %% ../../nbs/client/10_get_data.ipynb 6
async def looper(
    auth: dmda.DomoAuth,
    session: aiohttp.ClientSession,
    url,
    offset_params,
    arr_fn: callable,
    loop_until_end: bool = False,
    method="POST",
    body: dict = None,
    fixed_params: dict = None,
    offset_params_in_body: bool = False,
    body_fn=None,
    limit=1000,
    maximum=2000,
    debug_api: bool = False,
    debug_loop: bool = False
):
    allRows = []
    skip = 0
    isLoop = True

    if maximum < limit:
        limit = maximum

    while isLoop:
        params = fixed_params or {}

        if offset_params_in_body:
            body[offset_params.get("offset")] = skip
            body[offset_params.get("limit")] = limit

        else:
            params[offset_params.get("offset")] = skip
            params[offset_params.get("limit")] = limit

        if body_fn:
            body = body_fn(skip, limit)

        if debug_loop:
            print(
                f"\n🚀 Retrieving records {skip} through {skip + limit} via {url}")
            # pprint(params)

        res = await get_data(
            auth=auth,
            url=url,
            method=method,
            params=params,
            session=session,
            body=body,
            debug_api=debug_api,
        )

        newRecords = arr_fn(res)

        allRows += newRecords

        if loop_until_end and len(newRecords) != 0:
            maximum = maximum + limit

        if debug_loop:
            print({"all_rows": len(allRows), "new_records": len(newRecords)})

        if len(allRows) >= maximum or len(newRecords) == 0:
            if debug_loop:
                print(
                    f"\n🎉 Success - {len(allRows)} records retrieved from {url} in query looper\n")


            isLoop = False


        skip += len(newRecords)
        
        if skip + limit > maximum:
            limit = maximum - len(allRows)

            if debug_loop:
                print(f"skip: {skip}, limit: {limit}")
        
    return allRows

