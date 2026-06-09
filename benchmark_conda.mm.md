```mermaid
---
title: split-stages-plan
---
flowchart LR
	classDef param fill:#f96
	subgraph one-data
		datasets
	end
	subgraph two-filter
		filtering-r
		datasets --> filtering-r
		filtering-py
		datasets --> filtering-py
	end
	subgraph three-normalize
		normalization-r
		filtering-py --> normalization-r
		filtering-r --> normalization-r
		normalization-py
		filtering-py --> normalization-py
		filtering-r --> normalization-py
	end
	subgraph four-select
		selection-seurat
		normalization-py --> selection-seurat
		normalization-r --> selection-seurat
		selection-scrapper
		normalization-py --> selection-scrapper
		normalization-r --> selection-scrapper
	end
	subgraph five-pca
		pca-scanpy
		selection-scrapper --> pca-scanpy
		selection-seurat --> pca-scanpy
		pca-scrapper
		selection-scrapper --> pca-scrapper
		selection-seurat --> pca-scrapper
	end
	subgraph six-embedding-metrics
		embedding-metrics-py
		pca-scanpy --> embedding-metrics-py
		pca-scrapper --> embedding-metrics-py
		embedding-metrics-r
		pca-scanpy --> embedding-metrics-r
		pca-scrapper --> embedding-metrics-r
	end
	subgraph graph
		graph-scanpy
		pca-scanpy --> graph-scanpy
		pca-scrapper --> graph-scanpy
	end
	subgraph cluster
		cluster-scanpy
		graph-scanpy --> cluster-scanpy
	end
	subgraph cluster-metrics
		cluster-metrics-r
		cluster-scanpy --> cluster-metrics-r
	end
	subgraph seven-integrate
		integration-harmony
		pca-scanpy --> integration-harmony
		pca-scrapper --> integration-harmony
	end
	subgraph nine-annotate
		annotation-singler
		selection-scrapper --> annotation-singler
		selection-seurat --> annotation-singler
	end
	subgraph params_datasets
		datasets_paramset0[dataset_name:['be1']]
	end
	params_datasets:::param --o datasets
	subgraph params_filtering-r
		filtering-r_paramset0[filter_type:['manual', 'scrapper-auto']]
	end
	params_filtering-r:::param --o filtering-r
	subgraph params_filtering-py
		filtering-py_paramset0[filter_type:['manual']]
	end
	params_filtering-py:::param --o filtering-py
	subgraph params_normalization-r
		normalization-r_paramset0[normalization_type:['seurat_log1pCP10k', 'scuttle_geometricSizeFactors']]
	end
	params_normalization-r:::param --o normalization-r
	subgraph params_normalization-py
		normalization-py_paramset0[normalization_type:['scanpy_log1pCP10k']]
	end
	params_normalization-py:::param --o normalization-py
	subgraph params_selection-seurat
		selection-seurat_paramset0[batch_variable:['Sample'] selection_type:['seurat_vst', 'seurat_vst_batch'] number_selected:2000]
	end
	params_selection-seurat:::param --o selection-seurat
	subgraph params_selection-scrapper
		selection-scrapper_paramset0[number_selected:2000]
	end
	params_selection-scrapper:::param --o selection-scrapper
	subgraph params_pca-scanpy
		pca-scanpy_paramset0[n_components:50 solver:['arpack', 'randomized'] random_seed:42]
	end
	params_pca-scanpy:::param --o pca-scanpy
	subgraph params_pca-scrapper
		pca-scrapper_paramset0[n_components:50 solver:['exact', 'irlba', 'random'] random_seed:42]
	end
	params_pca-scrapper:::param --o pca-scrapper
	subgraph params_graph-scanpy
		graph-scanpy_paramset0[n_neighbors:15 random_seed:42 flavor:umap]
	end
	params_graph-scanpy:::param --o graph-scanpy
	subgraph params_cluster-scanpy
		cluster-scanpy_paramset0[resolution:[0.5, 1.0] random_seed:42]
	end
	params_cluster-scanpy:::param --o cluster-scanpy
	subgraph params_integration-harmony
		integration-harmony_paramset0[batch_variable:['Sample'] theta:[0.1, 0.2]]
	end
	params_integration-harmony:::param --o integration-harmony
	subgraph params_annotation-singler
		annotation-singler_paramset0[reference:['HumanPrimaryCellAtlasData', 'BlueprintEncodeData']]
	end
	params_annotation-singler:::param --o annotation-singler
```
