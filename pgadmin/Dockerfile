FROM dpage/pgadmin4:8.14

USER root

COPY ./custom_entrypoint.sh /custom_entrypoint.sh
COPY ./pgpass.template /pgpass.template
COPY ./servers.json /pgadmin4/servers.json

RUN touch /var/lib/pgadmin/pgpass && chown 5050:5050 /var/lib/pgadmin/pgpass && chmod 0600 /var/lib/pgadmin/pgpass && chmod a+rx /custom_entrypoint.sh

RUN apk add --no-cache gettext

USER pgadmin

ENTRYPOINT ["/custom_entrypoint.sh"]
