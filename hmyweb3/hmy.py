import inspect
from toolz import(
    functoolz,
)
from typing import (
    Any,
    Callable,
    Dict,
    List,
    TypeVar,
    Union,
)
from eth_typing import (
    BlockNumber,
    HexStr,
)
from hexbytes import (
    HexBytes,
)

from web3 import (
    Web3,
)
from web3._utils.blocks import (
    select_method_for_block_identifier,
)
from web3._utils.filters import (
    select_filter_method,
)
from web3._utils.method_formatters import (
    get_error_formatters,
    get_request_formatters,
    get_result_formatters,
)
from web3.eth import (
    Eth,
)
from web3.main import (
    get_default_modules,
)
from web3.method import (
    Method,
    default_root_munger,
)
from web3.module import (
    Module,
    ModuleV2,
)
from web3.types import (
    BlockData,
    BlockIdentifier,
    FilterParams,
    LogReceipt,
    Nonce,
    RPCEndpoint,
    SyncStatus,
    TxData,
    TxReceipt,
    Wei,
    _Hash32,
)

def get_eq_eth_method_name(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]]
) -> RPCEndpoint:
    if method_name.startswith('hmy_'):
        return method_name.replace('hmy_', 'eth_', 1)
    elif method_name.startswith('hmyv2_'):
        return method_name.replace('hmyv2_', 'eth_', 1)
    return method_name


REQUEST_FORMATTERS = {
    RPCEndpoint('hmyv2_getBalance'): functoolz.identity,
}

RESULT_FORMATTERS = {
    None: None,
}


def get_hmy_request_formatters(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]]
) -> Dict[str, Callable[..., Any]]:
    return REQUEST_FORMATTERS.get(method_name, get_request_formatters(get_eq_eth_method_name(method_name)))


def get_hmy_result_formatters(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]],
    module: Union["Module", "ModuleV2"],
) -> Dict[str, Callable[..., Any]]:
    return RESULT_FORMATTERS.get(method_name, get_result_formatters(get_eq_eth_method_name(method_name), module))


def get_hmy_error_formatters(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]]
) -> Callable[..., Any]:
    return get_error_formatters(get_eq_eth_method_name(method_name))


TFunc = TypeVar('TFunc', bound=Callable[..., Any])

class HmyMethod(Method[TFunc]):
    def __init__(self, *args, **kwargs):
        method_init_sig = inspect.signature(Method.__init__)
        method_init_applied = method_init_sig.bind(None, *args, **kwargs)

        request_formatters = method_init_applied.arguments.pop('request_formatters', get_hmy_request_formatters)
        result_formatters = method_init_applied.arguments.pop('result_formatters', get_hmy_result_formatters)
        error_formatters = method_init_applied.arguments.pop('error_formatters', get_hmy_error_formatters)

        method_init_applied.arguments['request_formatters'] = request_formatters
        method_init_applied.arguments['result_formatters'] = result_formatters
        method_init_applied.arguments['error_formatters'] = error_formatters

        super().__init__(*(method_init_applied.args[1:]), **method_init_applied.kwargs)
        self.error_formatters = error_formatters

class Hmy(Eth):
    is_syncing: HmyMethod[Callable[[], Union[SyncStatus, bool]]] = HmyMethod(
        RPCEndpoint('hmy_syncing'),
        mungers=None,
    )

    _gas_price: HmyMethod[Callable[[], Wei]] = HmyMethod(
        RPCEndpoint('hmyv2_gasPrice'),
        mungers=None,
    )

    _block_number: HmyMethod[Callable[[], BlockNumber]] = HmyMethod(
        RPCEndpoint('hmyv2_blockNumber'),
        mungers=None,
    )

    get_balance: HmyMethod[Callable[..., Wei]] = HmyMethod(
        RPCEndpoint('hmyv2_getBalance'),
        mungers=[default_root_munger],
    )

    get_storage_at: HmyMethod[Callable[..., HexBytes]] = HmyMethod(
        RPCEndpoint('hmy_getStorageAt'),
        mungers=[Eth.get_storage_at_munger],
    )

    get_code: HmyMethod[Callable[..., HexBytes]] = HmyMethod(
        RPCEndpoint('hmy_getCode'),
        mungers=[Eth.block_id_munger]
    )

    # TODO: v2
    """
    `eth_getBlockByHash`
    `eth_getBlockByNumber`
    """
    get_block: HmyMethod[Callable[..., BlockData]] = HmyMethod(
        method_choice_depends_on_args=select_method_for_block_identifier(
            if_predefined=RPCEndpoint('hmy_getBlockByNumber'),
            if_hash=RPCEndpoint('hmy_getBlockByHash'),
            if_number=RPCEndpoint('hmy_getBlockByNumber'),
        ),
        mungers=[Eth.get_block_munger],
    )

    """
    `eth_getBlockTransactionCountByHash`
    `eth_getBlockTransactionCountByNumber`
    """
    get_block_transaction_count: HmyMethod[Callable[[BlockIdentifier], int]] = HmyMethod(
        method_choice_depends_on_args=select_method_for_block_identifier(
            if_predefined=RPCEndpoint('hmyv2_getBlockTransactionCountByNumber'),
            if_hash=RPCEndpoint('hmyv2_getBlockTransactionCountByHash'),
            if_number=RPCEndpoint('hmyv2_getBlockTransactionCountByNumber'),
        ),
        mungers=[default_root_munger]
    )

    get_transaction: HmyMethod[Callable[[_Hash32], TxData]] = HmyMethod(
        RPCEndpoint('hmyv2_getTransactionByHash'),
        mungers=[default_root_munger]
    )

    get_transaction_by_block: HmyMethod[Callable[[BlockIdentifier, int], TxData]] = HmyMethod(
        method_choice_depends_on_args=select_method_for_block_identifier(
            if_predefined=RPCEndpoint('hmyv2_getTransactionByBlockNumberAndIndex'),
            if_hash=RPCEndpoint('hmyv2_getTransactionByBlockHashAndIndex'),
            if_number=RPCEndpoint('hmyv2_getTransactionByBlockNumberAndIndex'),
        ),
        mungers=[default_root_munger]
    )

    getTransactionReceipt: HmyMethod[Callable[[_Hash32], TxReceipt]] = HmyMethod(
        RPCEndpoint('hmyv2_getTransactionReceipt'),
        mungers=[default_root_munger]
    )

    get_transaction_count: HmyMethod[Callable[..., Nonce]] = HmyMethod(
        RPCEndpoint('hmyv2_getTransactionCount'),
        mungers=[Eth.block_id_munger],
    )

    send_raw_transaction: HmyMethod[Callable[[Union[HexStr, bytes]], HexBytes]] = HmyMethod(
        RPCEndpoint('hmyv2_sendRawTransaction'),
        mungers=[default_root_munger],
    )

    call: HmyMethod[Callable[..., Union[bytes, bytearray]]] = HmyMethod(
        RPCEndpoint('hmy_call'),
        mungers=[Eth.call_munger]
    )

    estimateGas: HmyMethod[Callable[..., Wei]] = HmyMethod(
        RPCEndpoint('hmy_estimateGas'),
        mungers=[Eth.estimate_gas_munger]
    )

    filter: HmyMethod[Callable[..., Any]] = HmyMethod(
        method_choice_depends_on_args=select_filter_method(
            if_new_block_filter=RPCEndpoint('hmy_newBlockFilter'),
            if_new_pending_transaction_filter=RPCEndpoint('hmy_newPendingTransactionFilter'),
            if_new_filter=RPCEndpoint('hmy_newFilter'),
        ),
        mungers=[Eth.filter_munger],
    )

    getFilterChanges: HmyMethod[Callable[[HexStr], List[LogReceipt]]] = HmyMethod(
        RPCEndpoint('hmy_getFilterChanges'),
        mungers=[default_root_munger]
    )

    getFilterLogs: HmyMethod[Callable[[HexStr], List[LogReceipt]]] = HmyMethod(
        RPCEndpoint('hmy_getFilterLogs'),
        mungers=[default_root_munger]
    )

    getLogs: HmyMethod[Callable[[FilterParams], List[LogReceipt]]] = HmyMethod(
        RPCEndpoint('hmy_getLogs'),
        mungers=[default_root_munger]
    )


class HmyWeb3(Web3):
    hmy: Hmy

    def __init__(self, *args, **kwargs) -> None:
        web3_init_sig = inspect.signature(Web3.__init__)
        web3_init_applied = web3_init_sig.bind(None, *args, **kwargs)

        modules = web3_init_applied.arguments.pop('modules', get_default_modules())
        if modules is None:
            modules = get_default_modules()
        modules["eth"] = (Hmy, )
        modules["hmy"] = (Hmy, )

        web3_init_applied.arguments['modules'] = modules

        super().__init__(*(web3_init_applied.args[1:]), **web3_init_applied.kwargs)
