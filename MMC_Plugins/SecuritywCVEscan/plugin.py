import logging

def init_plugin():
    logging.info('[SecuritywCVEscan] Plugin initialisé.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    init_plugin()
