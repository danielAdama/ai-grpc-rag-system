from schemas.search_schemas import MatchAnyOrInterval
import grpc

from config.logger import Logger
logger = Logger(__name__)

def _parse_filters(filters_str):
    if filters_str.startswith('"') and filters_str.endswith('"'):
        filters_str = filters_str[1:-1]
    filters = filters_str.split(':')
    if len(filters) == 2:
        key, value = filters
        return {str(key.strip()): MatchAnyOrInterval(any=[value.strip('[]')])}
    else:
        logger.warning("Invalid filter format")
        return None
    
def _handle_exception(api_name, context, ex):
    logger.error(f"Error in {api_name}: {str(ex)}")
    context.set_details(str(ex))
    context.set_code(grpc.StatusCode.UNKNOWN)
    return None