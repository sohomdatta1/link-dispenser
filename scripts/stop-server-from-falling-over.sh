#!/bin/bash
kubectl patch deployment link-dispenser -p "$(<~/link-dispenser/stop-falling-over.yaml)"