FROM neo4j:3.5
RUN apt-get update && apt-get install -y unzip
ENV APOC_VERSION 3.5.0.9
ENV APOC_URI https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/${APOC_VERSION}/apoc-${APOC_VERSION}-all.jar
ENV ALGO_URI https://s3-eu-west-1.amazonaws.com/com.neo4j.graphalgorithms.dist/neo4j-graph-algorithms-3.5.14.0-standalone.zip

RUN cd /var/lib/neo4j/plugins && wget $APOC_URI && wget $ALGO_URI \
	&& unzip neo4j-graph-algorithms-3.5.14.0-standalone.zip \
	&& rm *.zip


