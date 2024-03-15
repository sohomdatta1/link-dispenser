#!/bin/bash
kubectl patch deployment crawljob -p "$(<~/link-dispenser/stop-falling-over.yaml)"