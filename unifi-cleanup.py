import aiounifi,aiohttp
import asyncio,async_timeout
import os,sys,argparse,time,logging

LOGGER = logging.getLogger(__name__)

def signalling_callback(signal, data):
    LOGGER.info(f"{signal}, {data}")

async def unifi_controller(
    host, username, password, port, site, session, sslcontext, callback
):
    """Setup UniFi controller and verify credentials."""
    controller = aiounifi.Controller(
        host,
        username=username,
        password=password,
        port=port,
        site=site,
        websession=session,
        sslcontext=sslcontext,
        callback=callback,
    )

    try:
        with async_timeout.timeout(10):
            await controller.check_unifi_os()
            await controller.login()
        return controller

    except aiounifi.LoginRequired:
        LOGGER.warning(f"Connected to UniFi at {host} but couldn't log in")

    except aiounifi.Unauthorized:
        LOGGER.warning(f"Connected to UniFi at {host} but not registered")

    except (asyncio.TimeoutError, aiounifi.RequestError):
        LOGGER.exception(f"Error connecting to the UniFi controller at {host}")

    except aiounifi.AiounifiException:
        LOGGER.exception("Unknown UniFi communication error occurred")

async def get_extraneous_clients(clients):
    LOGGER.info(f"Found {len(clients)} MACs")
    empty_macs=[]
    for client in clients:
        if 'mac' in client and 'hostname' not in client and 'name' not in client and 'fixed_ip' not in client and ('tx_bytes' not in client or client['tx_bytes']==0) and ('rx_bytes' not in client or client['rx_bytes']==0):
            empty_macs.append(client['mac'])
    LOGGER.info(f"Found {len(empty_macs)} extraneous MACs")
    return empty_macs


async def main(host, username, password, port, site, sslcontext=False):
    """Main function."""
    LOGGER.info("Starting aioUniFi")

    websession = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))

    controller = await unifi_controller(
        host=host,
        username=username,
        password=password,
        port=port,
        site=site,
        session=websession,
        sslcontext=sslcontext,
        callback=signalling_callback,
    )

    if not controller:
        LOGGER.error("Couldn't connect to UniFi controller")
        await websession.close()
        return

    await controller.initialize()

    clients = await controller.request(method="GET",path="/stat/alluser",)
    empty_macs = await get_extraneous_clients(clients)

    payload = {
        'cmd': 'forget-sta',
        'macs': empty_macs
    }
    await controller.request(method="POST",path="/cmd/stamgr",json=payload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
    parser.add_argument("-p", "--port", type=int, default=8443)
    parser.add_argument("-s", "--site", type=str, default="default")
    parser.add_argument("-D", "--debug", action="store_true")
    args = parser.parse_args()

    loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    logging.basicConfig(format="%(message)s", level=loglevel)

    LOGGER.info(
        f"{args.host}, {args.username}, {args.password}, {args.port}, {args.site}"
    )

    try:
        asyncio.run(
            main(
                host=args.host,
                username=args.username,
                password=args.password,
                port=args.port,
                site=args.site,
            )
        )
    except KeyboardInterrupt:
        pass