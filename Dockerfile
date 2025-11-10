FROM frolvlad/alpine-python3:latest

RUN pip3 install requests && \
    rm -r /root/.cache

COPY smhi.py /smhi.py
COPY run.sh /run.sh
RUN chmod 777 /smhi.py /run.sh

ENTRYPOINT ["/run.sh"]
