require(pbgalaxy)

assertError <- function(expr) {
  tryCatch({{expr}; FALSE}, simpleError = function(e) {
    return(TRUE)
  })
}

TestHarness <- function(prefix = "") {
  tests <- list()

  getTime <- function(elt) {
    elt[["time"]][3]
  }
  getResult <- function(elt) {
    elt[["result"]]
  }
  printResults <- function() {
    mwidth <- max(nchar(names(tests))) + 5
    fmtString <- paste("\t%s:  %-", mwidth, "s %-10g %-10s\n", sep = "")

    cat(sprintf("%s Results for %d tests %s \n\n", paste(rep("-", 30), collapse = ""),
                length(tests), paste(rep("-", 30), collapse = "")))
    
    for (elt in names(tests)) {
      cat(sprintf(fmtString, prefix, elt, getTime(tests[[elt]]), getResult(tests[[elt]])))
    }
  }
  
  function(nm, test, action = c("test", "print", "throw")) {
    action <- match.arg(action)
    switch(action,
           test = {
             tm <- system.time({
               b <- tryCatch(test, simpleError = function(e) {
                 return(FALSE)
               })
             })
             tests[[nm]] <<- list("result" = b, "time" = tm)
           },
           print = {
             printResults()
           },
           throw = {
             errs <- ! sapply(tests, getResult)
             if (any(errs)) {
               stop(simpleError(paste("Tests in error:\n",
                                      paste(paste("\t", names(tests)[errs], sep = ""),
                                            collapse = "\n"), sep = "")))
             }
           })
  }
}

TH <- TestHarness("Merge")

## same total number of alignments.
checkMerged <- function(merged, parts) {
  TH('n alignments match', sum(sapply(parts, nrow))
     == nrow(merged))
  
  TH('movies match', all(table(getMovieName(merged)) == 
                         table(do.call(c, lapply(parts, getMovieName)))))
  TH('refs match', all(table(getFullRefNames(merged)) == 
                       table(do.call(c, lapply(parts, getFullRefNames)))))
  TH('molecule idxs match', all(sort(as.character(getMoleculeIndex(merged))) == 
                                sort(do.call(c, lapply(lapply(parts, getMoleculeIndex),
                                                       as.character)))))
  lapply(parts, function(cmpH5) {
    cat("processing\n\t:", cmpH5@fileName, "\n")
    midx <- which(getMovieName(merged) %in% getMovieName(cmpH5) &
                  getHoleNumbers(merged) %in% getHoleNumbers(cmpH5))
    pidx <- 1:nrow(cmpH5)
    
    o <- function(cmpH5, idx) 
      idx[order(cmpH5$fullRefName[idx], cmpH5$tStart[idx], cmpH5$tEnd[idx],
                cmpH5$rStart[idx], cmpH5$rEnd[idx])]
    widx <- sample(1:length(midx), size = .1*length(midx))
    midx <- o(merged, midx)
    pidx <- o(cmpH5, pidx)

    TH(paste('ref names match', basename(cmpH5@fileName)),
       all(getFullRefNames(merged, midx) ==
           getFullRefNames(cmpH5, pidx)))
    
    TH(paste('alignments match', basename(cmpH5@fileName)), 
       all.equal(getAlignments(cmpH5, pidx[widx]),
                 getAlignments(merged, midx[widx])))
  })
  TH(action = 'print')
}

inDir <- commandArgs()[7]
regex <- if (is.na(commandArgs()[8])) "aligned_reads" else commandArgs()[8]
print(commandArgs())

merged <- PacBioCmpH5(paste(inDir, paste(regex, ".cmp.h5", sep = ""), sep = "/"))
parts <- Sys.glob(paste(inDir, paste(regex, ".chunk*.cmp.h5", sep = ""), sep = "/"))
parts <- lapply(parts, function(a) tryCatch(PacBioCmpH5(a), simpleError = function(e) NULL))
parts <- Filter(Negate(is.null), parts)

checkMerged(merged, parts)

