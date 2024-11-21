init:
	docker-compose -f docker-compose-dependencies.yml up -d
	sleep 10
	curl -X POST "http://localhost:8080/apis/registry/v2/groups/sctd/artifacts" \
     -H "Content-Type: application/json" \
     -H "X-Registry-ArtifactType: AVRO" \
     -H "X-Registry-ArtifactId: sctd_systems_tower_demo_user" \
     -H "X-Registry-Name: sctd_systems_tower_demo_user" \
     --data-binary @producer-v1/sctd_systems_tower_demo_user-v1.avsc
	open http://localhost:8080

consumer1:
	docker-compose -f docker-compose-consumer-v1.yml up --build

consumer2:
	docker-compose -f docker-compose-consumer-v2.yml up --build

producer1:
	docker-compose -f docker-compose-producer-v1.yml up --build

producer2:
	docker-compose -f docker-compose-producer-v2.yml up --build

rm:
	docker-compose -f docker-compose-dependencies.yml down
	docker-compose -f docker-compose-consumer-v1.yml down
	docker-compose -f docker-compose-consumer-v2.yml down
	docker-compose -f docker-compose-producer-v1.yml down
	docker-compose -f docker-compose-producer-v2.yml down
