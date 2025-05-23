from __future__ import print_function
from __future__ import division
from past.utils import old_div
from kafka.errors import NoBrokersAvailable, KafkaUnavailableError
from kafka import KafkaClient, KafkaConsumer

import json
import sys
import traceback
import time
import argparse
import base64

from scutils.settings_wrapper import SettingsWrapper
from scutils.log_factory import LogFactory
from scutils.method_timer import MethodTimer
from scutils.argparse_helper import ArgparseHelper


def main():
    # initial main parser setup
    parser = argparse.ArgumentParser(
        description='Kafka Dump: Scrapy Cluster Kafka topic dump utility for '
                    'debugging.', add_help=False)
    parser.add_argument('-h', '--help', action=ArgparseHelper,
                        help='show this help message and exit')

    subparsers = parser.add_subparsers(help='commands', dest='command')

    # args to use for all commands
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('-kh', '--kafka-host', action='store', required=False,
                             help="The override Kafka host")
    base_parser.add_argument('-s', '--settings', action='store', required=False,
                             help="The settings file to read from",
                             default="localsettings.py")
    base_parser.add_argument('-ll', '--log-level', action='store', required=False,
                             help="The log level", default=None,
                             choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    # list command
    list_parser = subparsers.add_parser('list', help='List all Kafka topics',
                                        parents=[base_parser])

    # dump command
    dump_parser = subparsers.add_parser('dump', help='Dump a Kafka topic',
                                        parents=[base_parser])
    dump_parser.add_argument('-t', '--topic', action='store', required=True,
                             help="The Kafka topic to read from")
    dump_parser.add_argument('-c', '--consumer', action='store',
                             required=False, default=None,
                             help="The Kafka consumer id to use")
    dump_parser.add_argument('-b', '--from-beginning', action='store_const',
                             required=False, const=True,
                             help="Read the topic from the beginning")
    dump_parser.add_argument('-nb', '--no-body', action='store_const',
                             required=False, const=True, default=False,
                             help="Do not include the raw html 'body' key in"
                                  " the use_json dump of the topic")
    dump_parser.add_argument('-p', '--pretty', action='store_const',
                             required=False, const=True, default=False,
                             help="Pretty print the use_json objects consumed")
    dump_parser.add_argument('-d', '--decode-base64', action='store_const',
                             required=False, const=True, default=False,
                             help="Decode the base64 encoded raw html body")

    args = vars(parser.parse_args())

    wrapper = SettingsWrapper()
    settings = wrapper.load(args['settings'])

    kafka_host = args['kafka_host'] if args['kafka_host'] else settings['KAFKA_HOSTS']
    log_level = args['log_level'] if args['log_level'] else settings['LOG_LEVEL']
    logger = LogFactory.get_instance(level=log_level, name='kafkadump')

    if args['command'] == 'list':
        try:
            logger.info("Getting Kafka consumer")
            offset = 'latest'
            consumer = KafkaConsumer(
                bootstrap_servers=kafka_host,
                consumer_timeout_ms=settings['KAFKA_CONSUMER_TIMEOUT'],
                auto_offset_reset=offset,
                auto_commit_interval_ms=settings['KAFKA_CONSUMER_COMMIT_INTERVAL_MS'],
                enable_auto_commit=settings['KAFKA_CONSUMER_AUTO_COMMIT_ENABLE'],
                max_partition_fetch_bytes=settings['KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES'])
        except KafkaUnavailableError as ex:
            message = "An exception '{0}' occured. Arguments:\n{1!r}" \
                .format(type(ex).__name__, ex.args)
            logger.error(message)
            sys.exit(1)
        logger.info('Running list command')
        print("Topics:")
        for topic in list(consumer.topics()):
            print("-", topic)
        logger.info("Closing Kafka connection")
        try:
            consumer.close()
        except:
            # Exception is thrown when group_id is None.
            # See https://github.com/dpkp/kafka-python/issues/619
            pass
        return 0
    elif args['command'] == 'dump':
        logger.info('Running dump command')
        topic = args["topic"]
        consumer_id = args["consumer"]

        try:
            logger.info("Getting Kafka consumer {}".format(topic, consumer_id))

            offset = 'earliest' if args["from_beginning"] else 'latest'

            consumer = KafkaConsumer(
                topic,
                group_id=consumer_id,
                bootstrap_servers=kafka_host,
                value_deserializer=lambda m: m.decode('utf-8'),
                consumer_timeout_ms=settings['KAFKA_CONSUMER_TIMEOUT'],
                auto_offset_reset=offset,
                auto_commit_interval_ms=settings['KAFKA_CONSUMER_COMMIT_INTERVAL_MS'],
                enable_auto_commit=settings['KAFKA_CONSUMER_AUTO_COMMIT_ENABLE'],
                max_partition_fetch_bytes=settings['KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES'])

            # print("Topics:")
            # for topic in list(consumer.topics()):
            #     print("-", topic)

        except NoBrokersAvailable as ex:
            logger.error('Unable to connect to Kafka')
            sys.exit(1)

        num_records = 0
        total_bytes = 0
        item = None

        while True:
            try:
                for message in consumer:
                    # print(num_records, message)
                    if message is None:
                        logger.info("no message")
                        break
                    logger.info("Received message")
                    val = message.value
                    try:
                        item = json.loads(val)
                        print(num_records, 'encoding', item['encoding'])
                        if args['decode_base64'] and 'body' in item:
                            # item['body'] = base64.b64decode(item['body'].encode('utf-8'))
                            # item['body'] = str(base64.b64decode(item['body'].encode('utf-8')))
                            item['body'] = base64.b64decode(item['body']).decode('utf-8')

                        if args['no_body'] and 'body' in item:
                            del item['body']
                    except ValueError:
                        logger.info("Message is not a JSON object")
                        item = val
                    body_bytes = len(item)

                    if args['pretty']:
                        print(json.dumps(item, indent=4))
                    else:
                        print(item)

                    if num_records < 50:
                        with open("/tmp/page_%d_%s.html" % (num_records, item['encoding']), 'w') as fp:
                            fp.write(item["body"])

                    num_records = num_records + 1
                    total_bytes = total_bytes + body_bytes
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            # except:
            #     logger.error(traceback.print_exc())
            #     break

        total_mbs = old_div(float(total_bytes), (1024 * 1024))
        # if item is not None:
        #     print("Last item:")
        #     print(json.dumps(item, indent=4))
        if num_records > 0:
            logger.info("Num Records: {n}, Total MBs: {m}, kb per message: {kb}"
                        .format(n=num_records, m=total_mbs,
                                kb=(float(total_bytes) / num_records / 1024)))
        else:
            logger.info("No records consumed")
            num_records = 0

        logger.info("Closing Kafka connection")
        try:
            consumer.close()
        except:
            # Exception is thrown when group_id is None.
            # See https://github.com/dpkp/kafka-python/issues/619
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
