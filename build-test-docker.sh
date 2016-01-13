docker run --rm -v $(pwd):/build -w=/build \
	-e AWS_ACCESS_KEY_ID \
	-e AWS_SECRET_ACCESS_KEY \
	-e AWS_SESSION_TOKEN \
	snelis/tox sh /build/build-test.sh
