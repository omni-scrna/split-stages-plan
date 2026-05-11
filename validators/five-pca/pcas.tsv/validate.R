#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)

validate_file <- function(path) {
  ok <- TRUE

  tryCatch({
    df <- read.table(path, header = TRUE, sep = "\t", check.names = FALSE)

    if (colnames(df)[1] != "PC1") {
      stop(sprintf("first column must be 'PC1', got '%s'", colnames(df)[1]))
    }
    if (nrow(df) == 0) stop("empty file")
    if (ncol(df) < 10) stop("too few columns")
    if (anyNA(df[1, ])) stop("first data row contains non-numeric values in PC columns")

  }, error = function(e) {
    message(sprintf("FAIL\t%s\t%s", path, e$message))
    ok <<- FALSE
  })

  if (ok) {
    message(sprintf("OK\t%s", path))
  }
}

invisible(lapply(args, validate_file))
