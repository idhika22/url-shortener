#!/bin/bash

set -euo pipefail

TAG="${1:-}"

if [[ -z "$TAG" ]]; then
    echo "Usage:./scripts/deploy.sh <tag|rollback>"
    exit 1
fi

STATE_DIR=".deploy"

CURRENT_FILE="$STATE_DIR/current_tag"
PREVIOUS_FILE="$STATE_DIR/previous_tag"

mkdir -p "$STATE_DIR"

if [[ "$TAG" != "rollback" ]]; then
    echo "Deploying Version : $TAG"

    IMAGE_TAG="$TAG" docker compose pull app

    IMAGE_TAG="$TAG" docker compose up -d 

    echo "Checking Application health..."

    for attempt in {1..10};do
        if curl -fsS http://localhost:8080/health;then
            echo "Application is healthy"
            break
        fi

        if [[ $attempt -eq 10 ]];then
            echo "Health check failed after 10 attempts"
            echo "Trying to run ./scripts/deploy.sh rollback"
            exit 1
        fi

        echo "Attempt $attempt failed.Trying again in 3 seconds"
        sleep 3
    done

    if [[ -f "$CURRENT_FILE" ]]; then
        cp "$CURRENT_FILE" "$PREVIOUS_FILE"
    fi

    printf '%s\n' "$TAG" > "$CURRENT_FILE"

    echo "Deployment Successful"
    echo "Current Version: $TAG"

fi


if [[ "$TAG" == "rollback" ]];then
    if [[! -f "$PREVIOUS_FILE" ]];then
        echo "Error: No previous deployment available for rollback"
        exit 1
    fi


    ROLLBACK_TAG="$(cat "$PREVIOUS_FILE")"
    CURRENT_TAG="$(cat "$CURRENT_FILE")"

    echo "Rolling back from $CURRENT_TAG to $ROLLBACK_TAG"

    IMAGE_TAG="$ROLLBACK__TAG" docker compose pull app
    IMAGE_TAG="$ROLLBACK_TAG" docker compose up -d

    echo "Checking Application health..."

    for attempt in {1..10};do
        if curl -fsS http://localhost:8080/health;then
            echo "Application is healthy"
            break
        fi

        if [[ $attempt -eq 10 ]];then
            echo "Health check failed after 10 attempts"
            echo "Trying to run ./scripts/deploy.sh rollback"
            exit 1
        fi

        echo "Attempt $attempt failed.Trying again in 3 seconds"
        sleep 3

    done 

    printf '%s\n' "$ROLLBACK_TAG" > "$CURRENT_FILE"
    printf '%s\n' "$CURRENT_TAG" > "$PREVIOUS_FILE"

    echo "Rollback successful!"
    echo "Current version: $ROLLBACK_TAG"
    echo "Previous version: $CURRENT_TAG"

fi



