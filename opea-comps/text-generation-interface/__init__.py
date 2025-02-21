#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

# Document
from cores.proto.docarray import (
    Audio2TextDoc,
    Base64ByteStrDoc,
    DocPath,
    EmbedDoc,
    GeneratedDoc,
    LLMParamsDoc,
    SearchedDoc,
    SearchedMultimodalDoc,
    LVMSearchedMultimodalDoc,
    RerankedDoc,
    TextDoc,
    MetadataTextDoc,
    RAGASParams,
    RAGASScores,
    GraphDoc,
    LVMDoc,
    LVMVideoDoc,
    ImagePath,
    ImagesPath,
    VideoPath,
    ImageDoc,
    SDInputs,
    SDImg2ImgInputs,
    SDOutputs,
    TextImageDoc,
    #MultimodalDoc,
    EmbedMultimodalDoc,
    FactualityDoc,
    ScoreDoc,
    PIIRequestDoc,
    PIIResponseDoc,
    Audio2text,
    DocSumDoc,
)

# Constants
from cores.mega.constants import MegaServiceEndpoint, ServiceRoleType, ServiceType

# Microservice
from cores.mega.orchestrator import ServiceOrchestrator
from cores.mega.orchestrator_with_yaml import ServiceOrchestratorWithYaml
from cores.mega.micro_service import MicroService, register_microservice, opea_microservices

# Telemetry
from cores.telemetry.opea_telemetry import opea_telemetry

# Common
from cores.common.component import OpeaComponent, OpeaComponentRegistry, OpeaComponentLoader

# Statistics
from cores.mega.base_statistics import (
    statistics_dict, 
    register_statistics
)

# Logger
from cores.mega.logger import CustomLogger
