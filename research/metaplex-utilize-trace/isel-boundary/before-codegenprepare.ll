define void @_ZN14token_metadata9processor4uses7utilize15process_utilize17h9789c7990f4c0b83E(ptr noalias nocapture noundef sret(%244) dereferenceable(32) %0, ptr noalias noundef readonly align 1 dereferenceable(32) %1, ptr noalias noundef nonnull readonly align 8 %2, i64 noundef %3, i64 noundef %4) unnamed_addr #1 {
  %6 = alloca %3, align 8
  %7 = alloca %3, align 8
  %8 = alloca %319, align 8
  %9 = alloca %244, align 8
  %10 = alloca [7 x i32], align 4
  %11 = alloca %3, align 8
  %12 = alloca %3, align 8
  %13 = alloca %319, align 8
  %14 = alloca %244, align 8
  %15 = alloca [7 x i32], align 4
  %16 = alloca [1 x i8], align 1
  %17 = alloca [4 x { ptr, i64 }], align 8
  %18 = alloca %20, align 8
  %19 = alloca [4 x i32], align 8
  %20 = alloca %343, align 8
  %21 = alloca %392, align 8
  %22 = alloca [7 x i32], align 4
  %23 = alloca %270, align 8
  %24 = alloca %245, align 8
  %25 = alloca [27 x i8], align 1
  %26 = alloca %244, align 8
  %27 = alloca [7 x i32], align 4
  %28 = alloca %343, align 8
  %29 = alloca %20, align 8
  %30 = alloca [4 x i32], align 8
  %31 = alloca %60, align 8
  %32 = alloca %135, align 8
  %33 = alloca %315, align 8
  %34 = alloca [66 x i32], align 8
  %35 = alloca %257, align 8
  %36 = alloca %244, align 8
  %37 = alloca [7 x i32], align 4
  %38 = alloca %244, align 8
  %39 = alloca [7 x i32], align 4
  %40 = alloca %315, align 8
  %41 = alloca [66 x i32], align 8
  %42 = alloca %257, align 8
  %43 = alloca %20, align 8
  %44 = alloca [4 x i32], align 8
  %45 = alloca %20, align 8
  %46 = alloca [4 x i32], align 8
  %47 = alloca %20, align 8
  %48 = alloca [4 x i32], align 8
  %49 = alloca %20, align 8
  %50 = alloca [4 x i32], align 8
  %51 = alloca %20, align 8
  %52 = alloca [4 x i32], align 8
  %53 = alloca %20, align 8
  %54 = alloca [4 x i32], align 8
  %55 = alloca %20, align 8
  %56 = alloca [4 x i32], align 8
  %57 = alloca %20, align 8
  %58 = alloca [4 x i32], align 8
  %59 = alloca %9, align 8
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %59)
  %60 = getelementptr inbounds %3, ptr %2, i64 %3
  store ptr %60, ptr %59, align 8, !alias.scope !7903
  %61 = getelementptr inbounds { ptr, ptr }, ptr %59, i64 0, i32 1
  store ptr %2, ptr %61, align 8, !alias.scope !7903
  %62 = getelementptr inbounds %9, ptr %59, i64 0, i32 1
  store i64 0, ptr %62, align 8, !alias.scope !7903
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %58)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %57)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %57, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7908)
  %63 = load i32, ptr %57, align 8, !range !146, !alias.scope !7911, !noalias !7908, !noundef !4
  %64 = icmp eq i32 %63, 22
  br i1 %64, label %65, label %70

65:                                               ; preds = %5
  %66 = getelementptr inbounds %22, ptr %57, i64 0, i32 1
  %67 = load ptr, ptr %66, align 8, !alias.scope !7911, !noalias !7908, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %57)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %58)
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %56)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %55)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %55, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7913)
  %68 = load i32, ptr %55, align 8, !range !146, !alias.scope !7916, !noalias !7913, !noundef !4
  %69 = icmp eq i32 %68, 22
  br i1 %69, label %80, label %85

70:                                               ; preds = %5
  %71 = getelementptr inbounds i8, ptr %57, i64 4
  %72 = load i32, ptr %71, align 4, !alias.scope !7918
  %73 = getelementptr inbounds i8, ptr %57, i64 8
  %74 = load ptr, ptr %73, align 8, !alias.scope !7918
  %75 = getelementptr inbounds i8, ptr %57, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %58, ptr noundef nonnull align 8 dereferenceable(16) %75, i64 16, i1 false), !alias.scope !7918
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %57)
  %76 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %76, ptr noundef nonnull align 8 dereferenceable(16) %58, i64 16, i1 false)
  store i32 %63, ptr %0, align 8, !alias.scope !7919
  %77 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %72, ptr %77, align 4, !alias.scope !7919
  %78 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %74, ptr %78, align 8, !alias.scope !7919
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %58)
  br label %79

79:                                               ; preds = %179, %188, %153, %141, %127, %113, %99, %85, %70
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %59)
  br label %448

80:                                               ; preds = %65
  %81 = getelementptr inbounds %22, ptr %55, i64 0, i32 1
  %82 = load ptr, ptr %81, align 8, !alias.scope !7916, !noalias !7913, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %55)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %56)
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %54)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %53)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %53, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7923)
  %83 = load i32, ptr %53, align 8, !range !146, !alias.scope !7926, !noalias !7923, !noundef !4
  %84 = icmp eq i32 %83, 22
  br i1 %84, label %94, label %99

85:                                               ; preds = %65
  %86 = getelementptr inbounds i8, ptr %55, i64 4
  %87 = load i32, ptr %86, align 4, !alias.scope !7928
  %88 = getelementptr inbounds i8, ptr %55, i64 8
  %89 = load ptr, ptr %88, align 8, !alias.scope !7928
  %90 = getelementptr inbounds i8, ptr %55, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %56, ptr noundef nonnull align 8 dereferenceable(16) %90, i64 16, i1 false), !alias.scope !7928
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %55)
  %91 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %91, ptr noundef nonnull align 8 dereferenceable(16) %56, i64 16, i1 false)
  store i32 %68, ptr %0, align 8, !alias.scope !7929
  %92 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %87, ptr %92, align 4, !alias.scope !7929
  %93 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %89, ptr %93, align 8, !alias.scope !7929
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %56)
  br label %79

94:                                               ; preds = %80
  %95 = getelementptr inbounds %22, ptr %53, i64 0, i32 1
  %96 = load ptr, ptr %95, align 8, !alias.scope !7926, !noalias !7923, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %53)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %54)
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %52)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %51)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %51, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7933)
  %97 = load i32, ptr %51, align 8, !range !146, !alias.scope !7936, !noalias !7933, !noundef !4
  %98 = icmp eq i32 %97, 22
  br i1 %98, label %108, label %113

99:                                               ; preds = %80
  %100 = getelementptr inbounds i8, ptr %53, i64 4
  %101 = load i32, ptr %100, align 4, !alias.scope !7938
  %102 = getelementptr inbounds i8, ptr %53, i64 8
  %103 = load ptr, ptr %102, align 8, !alias.scope !7938
  %104 = getelementptr inbounds i8, ptr %53, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %54, ptr noundef nonnull align 8 dereferenceable(16) %104, i64 16, i1 false), !alias.scope !7938
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %53)
  %105 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %105, ptr noundef nonnull align 8 dereferenceable(16) %54, i64 16, i1 false)
  store i32 %83, ptr %0, align 8, !alias.scope !7939
  %106 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %101, ptr %106, align 4, !alias.scope !7939
  %107 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %103, ptr %107, align 8, !alias.scope !7939
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %54)
  br label %79

108:                                              ; preds = %94
  %109 = getelementptr inbounds %22, ptr %51, i64 0, i32 1
  %110 = load ptr, ptr %109, align 8, !alias.scope !7936, !noalias !7933, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %51)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %52)
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %50)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %49)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %49, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7943)
  %111 = load i32, ptr %49, align 8, !range !146, !alias.scope !7946, !noalias !7943, !noundef !4
  %112 = icmp eq i32 %111, 22
  br i1 %112, label %122, label %127

113:                                              ; preds = %94
  %114 = getelementptr inbounds i8, ptr %51, i64 4
  %115 = load i32, ptr %114, align 4, !alias.scope !7948
  %116 = getelementptr inbounds i8, ptr %51, i64 8
  %117 = load ptr, ptr %116, align 8, !alias.scope !7948
  %118 = getelementptr inbounds i8, ptr %51, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %52, ptr noundef nonnull align 8 dereferenceable(16) %118, i64 16, i1 false), !alias.scope !7948
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %51)
  %119 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %119, ptr noundef nonnull align 8 dereferenceable(16) %52, i64 16, i1 false)
  store i32 %97, ptr %0, align 8, !alias.scope !7949
  %120 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %115, ptr %120, align 4, !alias.scope !7949
  %121 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %117, ptr %121, align 8, !alias.scope !7949
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %52)
  br label %79

122:                                              ; preds = %108
  %123 = getelementptr inbounds %22, ptr %49, i64 0, i32 1
  %124 = load ptr, ptr %123, align 8, !alias.scope !7946, !noalias !7943, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %49)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %50)
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %48)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %47)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %47, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7953)
  %125 = load i32, ptr %47, align 8, !range !146, !alias.scope !7956, !noalias !7953, !noundef !4
  %126 = icmp eq i32 %125, 22
  br i1 %126, label %136, label %141

127:                                              ; preds = %108
  %128 = getelementptr inbounds i8, ptr %49, i64 4
  %129 = load i32, ptr %128, align 4, !alias.scope !7958
  %130 = getelementptr inbounds i8, ptr %49, i64 8
  %131 = load ptr, ptr %130, align 8, !alias.scope !7958
  %132 = getelementptr inbounds i8, ptr %49, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %50, ptr noundef nonnull align 8 dereferenceable(16) %132, i64 16, i1 false), !alias.scope !7958
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %49)
  %133 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %133, ptr noundef nonnull align 8 dereferenceable(16) %50, i64 16, i1 false)
  store i32 %111, ptr %0, align 8, !alias.scope !7959
  %134 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %129, ptr %134, align 4, !alias.scope !7959
  %135 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %131, ptr %135, align 8, !alias.scope !7959
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %50)
  br label %79

136:                                              ; preds = %122
  %137 = getelementptr inbounds %22, ptr %47, i64 0, i32 1
  %138 = load ptr, ptr %137, align 8, !alias.scope !7956, !noalias !7953, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %47)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %48)
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %46)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %45)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %45, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7963)
  %139 = load i32, ptr %45, align 8, !range !146, !alias.scope !7966, !noalias !7963, !noundef !4
  %140 = icmp eq i32 %139, 22
  br i1 %140, label %150, label %153

141:                                              ; preds = %122
  %142 = getelementptr inbounds i8, ptr %47, i64 4
  %143 = load i32, ptr %142, align 4, !alias.scope !7968
  %144 = getelementptr inbounds i8, ptr %47, i64 8
  %145 = load ptr, ptr %144, align 8, !alias.scope !7968
  %146 = getelementptr inbounds i8, ptr %47, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %48, ptr noundef nonnull align 8 dereferenceable(16) %146, i64 16, i1 false), !alias.scope !7968
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %47)
  %147 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %147, ptr noundef nonnull align 8 dereferenceable(16) %48, i64 16, i1 false)
  store i32 %125, ptr %0, align 8, !alias.scope !7969
  %148 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %143, ptr %148, align 4, !alias.scope !7969
  %149 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %145, ptr %149, align 8, !alias.scope !7969
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %48)
  br label %79

150:                                              ; preds = %136
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %45)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %46)
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %44)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %43)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %43, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7973)
  %151 = load i32, ptr %43, align 8, !range !146, !alias.scope !7976, !noalias !7973, !noundef !4
  %152 = icmp eq i32 %151, 22
  br i1 %152, label %162, label %179

153:                                              ; preds = %136
  %154 = getelementptr inbounds i8, ptr %45, i64 4
  %155 = load i32, ptr %154, align 4, !alias.scope !7978
  %156 = getelementptr inbounds i8, ptr %45, i64 8
  %157 = load ptr, ptr %156, align 8, !alias.scope !7978
  %158 = getelementptr inbounds i8, ptr %45, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %46, ptr noundef nonnull align 8 dereferenceable(16) %158, i64 16, i1 false), !alias.scope !7978
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %45)
  %159 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %159, ptr noundef nonnull align 8 dereferenceable(16) %46, i64 16, i1 false)
  store i32 %139, ptr %0, align 8, !alias.scope !7979
  %160 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %155, ptr %160, align 4, !alias.scope !7979
  %161 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %157, ptr %161, align 8, !alias.scope !7979
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %46)
  br label %79

162:                                              ; preds = %150
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %43)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %44)
  %163 = call noundef align 8 dereferenceable_or_null(48) ptr @"_ZN4core4iter8adapters8peekable17Peekable$LT$I$GT$7next_if17h8be795c6e429a654E"(ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  %164 = icmp eq ptr %163, null
  %165 = icmp eq i64 %3, 11
  %166 = icmp eq i64 %3, 10
  %167 = select i1 %164, i1 %166, i1 %165
  call void @llvm.lifetime.start.p0(i64 304, ptr nonnull %42)
  call void @llvm.lifetime.start.p0(i64 264, ptr nonnull %41)
  call void @llvm.lifetime.start.p0(i64 304, ptr nonnull %40)
  call void @_ZN14token_metadata5state20TokenMetadataAccount17from_account_info17hcfef9f224c5b6ff6E(ptr noalias nocapture noundef nonnull sret(%315) dereferenceable(304) %40, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %67) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7983)
  %168 = getelementptr inbounds %315, ptr %40, i64 0, i32 1
  %169 = load i32, ptr %168, align 8, !range !252, !alias.scope !7986, !noalias !7983, !noundef !4
  %170 = icmp eq i32 %169, 2
  br i1 %170, label %171, label %172

171:                                              ; preds = %162
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %41, ptr noundef nonnull align 8 dereferenceable(32) %40, i64 32, i1 false), !alias.scope !7988
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %40)
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %0, ptr noundef nonnull align 8 dereferenceable(32) %41, i64 32, i1 false)
  call void @llvm.lifetime.end.p0(i64 264, ptr nonnull %41)
  br label %188

172:                                              ; preds = %162
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(264) %41, ptr noundef nonnull align 8 dereferenceable(264) %40, i64 264, i1 false), !alias.scope !7988
  %173 = getelementptr inbounds i8, ptr %40, i64 268
  %174 = getelementptr inbounds i8, ptr %42, i64 268
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(36) %174, ptr noundef nonnull align 4 dereferenceable(36) %173, i64 36, i1 false)
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %40)
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(264) %42, ptr noundef nonnull align 8 dereferenceable(264) %41, i64 264, i1 false)
  %175 = getelementptr inbounds i8, ptr %42, i64 264
  store i32 %169, ptr %175, align 8
  call void @llvm.lifetime.end.p0(i64 264, ptr nonnull %41)
  %176 = getelementptr inbounds %257, ptr %42, i64 0, i32 11
  %177 = load i32, ptr %176, align 8, !range !219, !alias.scope !7989, !noundef !4
  %178 = icmp eq i32 %177, 3
  br i1 %178, label %193, label %189

179:                                              ; preds = %150
  %180 = getelementptr inbounds i8, ptr %43, i64 4
  %181 = load i32, ptr %180, align 4, !alias.scope !7992
  %182 = getelementptr inbounds i8, ptr %43, i64 8
  %183 = load ptr, ptr %182, align 8, !alias.scope !7992
  %184 = getelementptr inbounds i8, ptr %43, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %44, ptr noundef nonnull align 8 dereferenceable(16) %184, i64 16, i1 false), !alias.scope !7992
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %43)
  %185 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %185, ptr noundef nonnull align 8 dereferenceable(16) %44, i64 16, i1 false)
  store i32 %151, ptr %0, align 8, !alias.scope !7993
  %186 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %181, ptr %186, align 4, !alias.scope !7993
  %187 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %183, ptr %187, align 8, !alias.scope !7993
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %44)
  br label %79

188:                                              ; preds = %195, %171
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %42)
  br label %79

189:                                              ; preds = %172
  %190 = getelementptr inbounds %257, ptr %42, i64 0, i32 8
  %191 = load i32, ptr %190, align 4, !range !456, !noundef !4
  %192 = icmp eq i32 %191, 6
  br i1 %192, label %201, label %197

193:                                              ; preds = %172
  store i32 0, ptr %0, align 8
  %194 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 85, ptr %194, align 4
  br label %195

195:                                              ; preds = %238, %235, %211, %206, %201, %193
  %196 = getelementptr inbounds %257, ptr %42, i64 0, i32 4
  call fastcc void @"_ZN4core3ptr54drop_in_place$LT$token_metadata..state..data..Data$GT$17h361e34b2f1c25fb1E"(ptr noundef nonnull %196) #32
  br label %188

197:                                              ; preds = %189
  switch i32 %191, label %201 [
    i32 0, label %198
    i32 3, label %198
    i32 4, label %198
    i32 5, label %198
  ]

198:                                              ; preds = %197, %197, %197, %197
  %199 = load ptr, ptr %138, align 8, !nonnull !4, !align !37, !noundef !4
  %200 = tail call fastcc noundef zeroext i1 @_ZN4core3cmp9PartialEq2ne17h0d0d6ae917ee2100E(ptr noalias noundef nonnull readonly align 1 dereferenceable(32) %199, ptr noalias noundef nonnull readonly align 1 dereferenceable(32) @anon.3b777117c5a3ed67056920cb3eb2bd37.172) #32
  br i1 %200, label %206, label %203

201:                                              ; preds = %197, %189
  store i32 0, ptr %0, align 8
  %202 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 135, ptr %202, align 4
  br label %195

203:                                              ; preds = %198
  call void @llvm.lifetime.start.p0(i64 28, ptr nonnull %39)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %38)
  call void @_ZN9mpl_utils10assertions13assert_signer17hc5021f06096037b1E(ptr noalias nocapture noundef nonnull sret(%244) dereferenceable(32) %38, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %110) #32
  tail call void @llvm.experimental.noalias.scope.decl(metadata !7997)
  %204 = load i32, ptr %38, align 8, !range !146, !alias.scope !8000, !noalias !7997, !noundef !4
  %205 = icmp eq i32 %204, 22
  br i1 %205, label %208, label %211

206:                                              ; preds = %198
  store i32 0, ptr %0, align 8
  %207 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 62, ptr %207, align 4
  br label %195

208:                                              ; preds = %203
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %38)
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %39)
  call void @llvm.lifetime.start.p0(i64 28, ptr nonnull %37)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %36)
  call void @_ZN14token_metadata10assertions8metadata24assert_currently_holding17h9773fdd27308f043E(ptr noalias nocapture noundef nonnull sret(%244) dereferenceable(32) %36, ptr noalias noundef nonnull readonly align 1 dereferenceable(32) %1, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %124, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %67, ptr noalias noundef nonnull readonly align 8 dereferenceable(304) %42, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %96, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %82) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8002)
  %209 = load i32, ptr %36, align 8, !range !146, !alias.scope !8005, !noalias !8002, !noundef !4
  %210 = icmp eq i32 %209, 22
  br i1 %210, label %214, label %235

211:                                              ; preds = %203
  %212 = getelementptr inbounds i8, ptr %38, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %39, ptr noundef nonnull align 4 dereferenceable(28) %212, i64 28, i1 false), !alias.scope !8007
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %38)
  %213 = getelementptr inbounds i8, ptr %0, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %213, ptr noundef nonnull align 4 dereferenceable(28) %39, i64 28, i1 false)
  store i32 %204, ptr %0, align 8, !alias.scope !8008
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %39)
  br label %195

214:                                              ; preds = %208
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %36)
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %37)
  call void @llvm.lifetime.start.p0(i64 304, ptr nonnull %35)
  call void @llvm.lifetime.start.p0(i64 264, ptr nonnull %34)
  call void @llvm.lifetime.start.p0(i64 304, ptr nonnull %33)
  call void @_ZN14token_metadata5state20TokenMetadataAccount17from_account_info17hcfef9f224c5b6ff6E(ptr noalias nocapture noundef nonnull sret(%315) dereferenceable(304) %33, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %67) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8012)
  %215 = getelementptr inbounds %315, ptr %33, i64 0, i32 1
  %216 = load i32, ptr %215, align 8, !range !252, !alias.scope !8015, !noalias !8012, !noundef !4
  %217 = icmp eq i32 %216, 2
  br i1 %217, label %218, label %219

218:                                              ; preds = %214
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %34, ptr noundef nonnull align 8 dereferenceable(32) %33, i64 32, i1 false), !alias.scope !8017
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %33)
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %0, ptr noundef nonnull align 8 dereferenceable(32) %34, i64 32, i1 false)
  call void @llvm.lifetime.end.p0(i64 264, ptr nonnull %34)
  br label %238

219:                                              ; preds = %214
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(264) %34, ptr noundef nonnull align 8 dereferenceable(264) %33, i64 264, i1 false), !alias.scope !8017
  %220 = getelementptr inbounds i8, ptr %33, i64 268
  %221 = getelementptr inbounds i8, ptr %35, i64 268
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(36) %221, ptr noundef nonnull align 4 dereferenceable(36) %220, i64 36, i1 false)
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %33)
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(264) %35, ptr noundef nonnull align 8 dereferenceable(264) %34, i64 264, i1 false)
  %222 = getelementptr inbounds i8, ptr %35, i64 264
  store i32 %216, ptr %222, align 8
  call void @llvm.lifetime.end.p0(i64 264, ptr nonnull %34)
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %32)
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %31)
  %223 = getelementptr inbounds %257, ptr %35, i64 0, i32 11
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(24) %31, ptr noundef nonnull align 8 dereferenceable(24) %223, i64 24, i1 false)
  call fastcc void @"_ZN4core6option15Option$LT$T$GT$6unwrap17h43982a0059e73655E"(ptr noalias nocapture noundef nonnull sret(%135) dereferenceable(24) %32, ptr noalias nocapture noundef nonnull dereferenceable(24) %31, ptr noalias noundef nonnull readonly align 8 dereferenceable(24) @anon.3b777117c5a3ed67056920cb3eb2bd37.369) #32
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %31)
  %224 = load i32, ptr %32, align 8, !range !252, !alias.scope !8018, !noalias !8021, !noundef !4
  %225 = icmp eq i32 %224, 0
  %226 = icmp eq i64 %4, 0
  %227 = getelementptr inbounds %135, ptr %32, i64 0, i32 3
  %228 = load i64, ptr %227, align 8
  %229 = icmp ult i64 %228, %4
  %230 = select i1 %226, i1 true, i1 %229
  %231 = getelementptr inbounds %135, ptr %32, i64 0, i32 2
  %232 = load i64, ptr %231, align 8
  %233 = icmp ult i64 %232, %4
  %234 = select i1 %230, i1 true, i1 %233
  br i1 %234, label %239, label %243

235:                                              ; preds = %208
  %236 = getelementptr inbounds i8, ptr %36, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %37, ptr noundef nonnull align 4 dereferenceable(28) %236, i64 28, i1 false), !alias.scope !8023
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %36)
  %237 = getelementptr inbounds i8, ptr %0, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %237, ptr noundef nonnull align 4 dereferenceable(28) %37, i64 28, i1 false)
  store i32 %209, ptr %0, align 8, !alias.scope !8024
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %37)
  br label %195

238:                                              ; preds = %241, %218
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %35)
  br label %195

239:                                              ; preds = %219
  store i32 0, ptr %0, align 8
  %240 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 86, ptr %240, align 4
  br label %241

241:                                              ; preds = %363, %381, %274, %292, %445, %408, %441, %436, %351, %257, %239
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %32)
  %242 = getelementptr inbounds %257, ptr %35, i64 0, i32 4
  call fastcc void @"_ZN4core3ptr54drop_in_place$LT$token_metadata..state..data..Data$GT$17h361e34b2f1c25fb1E"(ptr noundef nonnull %242) #32
  br label %238

243:                                              ; preds = %219
  %244 = sub i64 %232, %4
  store i32 %224, ptr %223, align 8
  %245 = getelementptr inbounds %257, ptr %35, i64 0, i32 11, i32 1, i64 1
  store i64 %244, ptr %245, align 8
  %246 = getelementptr inbounds %257, ptr %35, i64 0, i32 11, i32 1, i64 3
  store i64 %228, ptr %246, align 8
  br i1 %167, label %249, label %247

247:                                              ; preds = %243
  %248 = call fastcc noundef zeroext i1 @"_ZN4core3cmp5impls69_$LT$impl$u20$core..cmp..PartialEq$LT$$RF$B$GT$$u20$for$u20$$RF$A$GT$2ne17h034b8f2a183c21c2E"(ptr noalias noundef nonnull readonly align 8 dereferenceable(8) %110, ptr noalias noundef nonnull readonly align 8 dereferenceable(8) %124) #32
  br i1 %248, label %351, label %348

249:                                              ; preds = %243
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %30)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %29)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %29, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8028)
  %250 = load i32, ptr %29, align 8, !range !146, !alias.scope !8031, !noalias !8028, !noundef !4
  %251 = icmp eq i32 %250, 22
  br i1 %251, label %252, label %257

252:                                              ; preds = %249
  %253 = getelementptr inbounds %22, ptr %29, i64 0, i32 1
  %254 = load ptr, ptr %253, align 8, !alias.scope !8031, !noalias !8028, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %29)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %30)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %28)
  call void @_ZN14solana_program12account_info11AccountInfo19try_borrow_mut_data17hcf238957d2f67b88E(ptr noalias nocapture noundef nonnull sret(%343) dereferenceable(32) %28, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %254) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8033)
  %255 = load i32, ptr %28, align 8, !range !146, !alias.scope !8036, !noalias !8033, !noundef !4
  %256 = icmp eq i32 %255, 22
  br i1 %256, label %266, label %274

257:                                              ; preds = %249
  %258 = getelementptr inbounds i8, ptr %29, i64 4
  %259 = load i32, ptr %258, align 4, !alias.scope !8038
  %260 = getelementptr inbounds i8, ptr %29, i64 8
  %261 = load ptr, ptr %260, align 8, !alias.scope !8038
  %262 = getelementptr inbounds i8, ptr %29, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %30, ptr noundef nonnull align 8 dereferenceable(16) %262, i64 16, i1 false), !alias.scope !8038
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %29)
  %263 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %263, ptr noundef nonnull align 8 dereferenceable(16) %30, i64 16, i1 false)
  store i32 %250, ptr %0, align 8, !alias.scope !8039
  %264 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %259, ptr %264, align 4, !alias.scope !8039
  %265 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %261, ptr %265, align 8, !alias.scope !8039
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %30)
  br label %241

266:                                              ; preds = %252
  %267 = getelementptr inbounds %347, ptr %28, i64 0, i32 1
  %268 = load ptr, ptr %267, align 8, !alias.scope !8036, !noalias !8033, !nonnull !4, !noundef !4
  %269 = getelementptr inbounds %347, ptr %28, i64 0, i32 1, i32 1
  %270 = load ptr, ptr %269, align 8, !alias.scope !8036, !noalias !8033, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %28)
  %271 = getelementptr inbounds { ptr, i64 }, ptr %268, i64 0, i32 1
  %272 = load i64, ptr %271, align 8, !noundef !4
  %273 = icmp eq i64 %272, 0
  br i1 %273, label %290, label %287

274:                                              ; preds = %252
  %275 = getelementptr inbounds i8, ptr %28, i64 4
  %276 = load i32, ptr %275, align 4, !alias.scope !8043
  %277 = getelementptr inbounds i8, ptr %28, i64 8
  %278 = load ptr, ptr %277, align 8, !alias.scope !8043
  %279 = getelementptr inbounds i8, ptr %28, i64 16
  %280 = load ptr, ptr %279, align 8, !alias.scope !8043
  %281 = getelementptr inbounds i8, ptr %28, i64 24
  %282 = load i64, ptr %281, align 8, !alias.scope !8043
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %28)
  store i32 %255, ptr %0, align 8, !alias.scope !8044
  %283 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %276, ptr %283, align 4, !alias.scope !8044
  %284 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %278, ptr %284, align 8, !alias.scope !8044
  %285 = getelementptr inbounds i8, ptr %0, i64 16
  store ptr %280, ptr %285, align 8, !alias.scope !8044
  %286 = getelementptr inbounds i8, ptr %0, i64 24
  store i64 %282, ptr %286, align 8, !alias.scope !8044
  br label %241

287:                                              ; preds = %266
  call void @llvm.lifetime.start.p0(i64 28, ptr nonnull %27)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %26)
  call void @_ZN14token_metadata10assertions4misc15assert_owned_by17h280f82a67421a794E(ptr noalias nocapture noundef nonnull sret(%244) dereferenceable(32) %26, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %254, ptr noalias noundef nonnull readonly align 1 dereferenceable(32) %1) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8048)
  %288 = load i32, ptr %26, align 8, !range !146, !alias.scope !8051, !noalias !8048, !noundef !4
  %289 = icmp eq i32 %288, 22
  br i1 %289, label %295, label %298

290:                                              ; preds = %266
  store i32 0, ptr %0, align 8, !alias.scope !8053
  %291 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 84, ptr %291, align 4, !alias.scope !8053
  br label %292

292:                                              ; preds = %308, %326, %298, %290
  %293 = load i64, ptr %270, align 8, !noalias !8057, !noundef !4
  %294 = add i64 %293, 1
  store i64 %294, ptr %270, align 8, !noalias !8057
  br label %241

295:                                              ; preds = %287
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %26)
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %27)
  call void @llvm.lifetime.start.p0(i64 27, ptr nonnull %25)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %24)
  call void @_ZN14token_metadata10assertions4uses31assert_use_authority_derivation17h9f9a4e6bb881fba5E(ptr noalias nocapture noundef nonnull sret(%245) dereferenceable(32) %24, ptr noalias noundef nonnull readonly align 1 dereferenceable(32) %1, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %254, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %110, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %96) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8060)
  %296 = load i32, ptr %24, align 8, !range !146, !alias.scope !8063, !noalias !8060, !noundef !4
  %297 = icmp eq i32 %296, 22
  br i1 %297, label %301, label %308

298:                                              ; preds = %287
  %299 = getelementptr inbounds i8, ptr %26, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %27, ptr noundef nonnull align 4 dereferenceable(28) %299, i64 28, i1 false), !alias.scope !8065
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %26)
  %300 = getelementptr inbounds i8, ptr %0, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %300, ptr noundef nonnull align 4 dereferenceable(28) %27, i64 28, i1 false)
  store i32 %288, ptr %0, align 8, !alias.scope !8066
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %27)
  br label %292

301:                                              ; preds = %295
  %302 = getelementptr inbounds %246, ptr %24, i64 0, i32 1
  %303 = load i8, ptr %302, align 4, !alias.scope !8063, !noalias !8060, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %24)
  call void @llvm.lifetime.end.p0(i64 27, ptr nonnull %25)
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %23)
  call void @llvm.lifetime.start.p0(i64 28, ptr nonnull %22)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %21)
  %304 = load ptr, ptr %268, align 8, !nonnull !4, !align !37, !noundef !4
  %305 = load i64, ptr %271, align 8, !noundef !4
  call void @_ZN14token_metadata5state4uses18UseAuthorityRecord10from_bytes17h225c712c2b66acceE(ptr noalias nocapture noundef nonnull sret(%392) dereferenceable(32) %21, ptr noalias noundef nonnull readonly align 1 %304, i64 noundef %305) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8070)
  %306 = load i32, ptr %21, align 8, !range !146, !alias.scope !8073, !noalias !8070, !noundef !4
  %307 = icmp eq i32 %306, 22
  br i1 %307, label %314, label %323

308:                                              ; preds = %295
  %309 = getelementptr inbounds i8, ptr %24, i64 4
  %310 = load i8, ptr %309, align 4, !alias.scope !8075
  %311 = getelementptr inbounds i8, ptr %24, i64 5
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 1 dereferenceable(27) %25, ptr noundef nonnull align 1 dereferenceable(27) %311, i64 27, i1 false), !alias.scope !8075
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %24)
  %312 = getelementptr inbounds i8, ptr %0, i64 5
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 1 dereferenceable(27) %312, ptr noundef nonnull align 1 dereferenceable(27) %25, i64 27, i1 false)
  store i32 %296, ptr %0, align 8, !alias.scope !8076
  %313 = getelementptr inbounds i8, ptr %0, i64 4
  store i8 %310, ptr %313, align 4, !alias.scope !8076
  call void @llvm.lifetime.end.p0(i64 27, ptr nonnull %25)
  br label %292

314:                                              ; preds = %301
  %315 = getelementptr inbounds %393, ptr %21, i64 0, i32 1
  %316 = getelementptr inbounds i8, ptr %22, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(24) %316, ptr noundef nonnull align 8 dereferenceable(24) %315, i64 24, i1 false), !alias.scope !8080
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %21)
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(24) %23, ptr noundef nonnull align 4 dereferenceable(24) %316, i64 24, i1 false)
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %22)
  %317 = getelementptr inbounds %270, ptr %23, i64 0, i32 3
  %318 = load i8, ptr %317, align 8, !alias.scope !8081, !noundef !4
  %319 = icmp eq i8 %318, 0
  %320 = load i32, ptr %23, align 8, !alias.scope !8081
  %321 = icmp eq i32 %320, 8
  %322 = select i1 %319, i1 %321, i1 false
  br i1 %322, label %329, label %327

323:                                              ; preds = %301
  %324 = getelementptr inbounds i8, ptr %21, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %22, ptr noundef nonnull align 4 dereferenceable(28) %324, i64 28, i1 false), !alias.scope !8080
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %21)
  %325 = getelementptr inbounds i8, ptr %0, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %325, ptr noundef nonnull align 4 dereferenceable(28) %22, i64 28, i1 false)
  store i32 %306, ptr %0, align 8, !alias.scope !8084
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %22)
  br label %326

326:                                              ; preds = %347, %342, %334, %323
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %23)
  br label %292

327:                                              ; preds = %314
  %328 = icmp eq i8 %318, %303
  br i1 %328, label %330, label %334

329:                                              ; preds = %314
  store i8 %303, ptr %317, align 8
  br label %330

330:                                              ; preds = %329, %327
  %331 = getelementptr inbounds %270, ptr %23, i64 0, i32 2
  %332 = load i64, ptr %331, align 8, !noundef !4
  %333 = icmp ult i64 %332, %4
  br i1 %333, label %342, label %336

334:                                              ; preds = %327
  store i32 0, ptr %0, align 8, !alias.scope !8088
  %335 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 89, ptr %335, align 4, !alias.scope !8088
  br label %326

336:                                              ; preds = %330
  %337 = sub i64 %332, %4
  store i64 %337, ptr %331, align 8
  %338 = load ptr, ptr %268, align 8, !nonnull !4, !align !37, !noundef !4
  %339 = load i64, ptr %271, align 8, !noundef !4
  %340 = call noundef ptr @_ZN5borsh3ser7helpers9to_writer17hfa629f22abad9120E(ptr noalias noundef nonnull align 1 %338, i64 noundef %339, ptr noalias noundef nonnull readonly align 8 dereferenceable(24) %23) #32
  %341 = icmp eq ptr %340, null
  br i1 %341, label %344, label %347

342:                                              ; preds = %330
  store i32 0, ptr %0, align 8, !alias.scope !8092
  %343 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 86, ptr %343, align 4, !alias.scope !8092
  br label %326

344:                                              ; preds = %336
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %23)
  %345 = load i64, ptr %270, align 8, !noalias !8095, !noundef !4
  %346 = add i64 %345, 1
  store i64 %346, ptr %270, align 8, !noalias !8095
  br label %348

347:                                              ; preds = %336
  call void @"_ZN112_$LT$solana_program..program_error..ProgramError$u20$as$u20$core..convert..From$LT$std..io..error..Error$GT$$GT$4from17h745c2ba68ce6a10fE"(ptr noalias nocapture noundef nonnull sret(%21) dereferenceable(32) %0, ptr noundef nonnull %340) #32
  br label %326

348:                                              ; preds = %247, %344
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %20)
  call void @_ZN14solana_program12account_info11AccountInfo19try_borrow_mut_data17hcf238957d2f67b88E(ptr noalias nocapture noundef nonnull sret(%343) dereferenceable(32) %20, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %67) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8098)
  %349 = load i32, ptr %20, align 8, !range !146, !alias.scope !8101, !noalias !8098, !noundef !4
  %350 = icmp eq i32 %349, 22
  br i1 %350, label %353, label %363

351:                                              ; preds = %247
  store i32 0, ptr %0, align 8
  %352 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 98, ptr %352, align 4
  br label %241

353:                                              ; preds = %348
  %354 = getelementptr inbounds %347, ptr %20, i64 0, i32 1
  %355 = load ptr, ptr %354, align 8, !alias.scope !8101, !noalias !8098, !nonnull !4, !noundef !4
  %356 = getelementptr inbounds %347, ptr %20, i64 0, i32 1, i32 1
  %357 = load ptr, ptr %356, align 8, !alias.scope !8101, !noalias !8098, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %20)
  %358 = load ptr, ptr %355, align 8, !nonnull !4, !align !37, !noundef !4
  %359 = getelementptr inbounds { ptr, i64 }, ptr %355, i64 0, i32 1
  %360 = load i64, ptr %359, align 8, !noundef !4
  %361 = call noundef ptr @_ZN14token_metadata5state8metadata8Metadata4save17h9a6561ae9bd1b989E(ptr noalias noundef nonnull readonly align 8 dereferenceable(304) %35, ptr noalias noundef nonnull align 1 %358, i64 noundef %360) #32
  %362 = icmp eq ptr %361, null
  br i1 %362, label %376, label %381

363:                                              ; preds = %348
  %364 = getelementptr inbounds i8, ptr %20, i64 4
  %365 = load i32, ptr %364, align 4, !alias.scope !8103
  %366 = getelementptr inbounds i8, ptr %20, i64 8
  %367 = load ptr, ptr %366, align 8, !alias.scope !8103
  %368 = getelementptr inbounds i8, ptr %20, i64 16
  %369 = load ptr, ptr %368, align 8, !alias.scope !8103
  %370 = getelementptr inbounds i8, ptr %20, i64 24
  %371 = load i64, ptr %370, align 8, !alias.scope !8103
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %20)
  store i32 %349, ptr %0, align 8, !alias.scope !8104
  %372 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %365, ptr %372, align 4, !alias.scope !8104
  %373 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %367, ptr %373, align 8, !alias.scope !8104
  %374 = getelementptr inbounds i8, ptr %0, i64 16
  store ptr %369, ptr %374, align 8, !alias.scope !8104
  %375 = getelementptr inbounds i8, ptr %0, i64 24
  store i64 %371, ptr %375, align 8, !alias.scope !8104
  br label %241

376:                                              ; preds = %353
  %377 = load i64, ptr %357, align 8, !noalias !8108, !noundef !4
  %378 = add i64 %377, 1
  store i64 %378, ptr %357, align 8, !noalias !8108
  %379 = icmp eq i64 %232, %4
  %380 = and i1 %225, %379
  br i1 %380, label %387, label %384

381:                                              ; preds = %353
  call void @"_ZN112_$LT$solana_program..program_error..ProgramError$u20$as$u20$core..convert..From$LT$std..io..error..Error$GT$$GT$4from17h745c2ba68ce6a10fE"(ptr noalias nocapture noundef nonnull sret(%21) dereferenceable(32) %0, ptr noundef nonnull %361) #32
  %382 = load i64, ptr %357, align 8, !noalias !8111, !noundef !4
  %383 = add i64 %382, 1
  store i64 %383, ptr %357, align 8, !noalias !8111
  br label %241

384:                                              ; preds = %440, %444, %376
  store i32 22, ptr %0, align 8
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %32)
  %385 = getelementptr inbounds %257, ptr %35, i64 0, i32 4
  call fastcc void @"_ZN4core3ptr54drop_in_place$LT$token_metadata..state..data..Data$GT$17h361e34b2f1c25fb1E"(ptr noundef nonnull %385) #32
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %35)
  %386 = getelementptr inbounds %257, ptr %42, i64 0, i32 4
  call fastcc void @"_ZN4core3ptr54drop_in_place$LT$token_metadata..state..data..Data$GT$17h361e34b2f1c25fb1E"(ptr noundef nonnull %386) #32
  call void @llvm.lifetime.end.p0(i64 304, ptr nonnull %42)
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %59)
  br label %448

387:                                              ; preds = %376
  br i1 %167, label %396, label %388

388:                                              ; preds = %387
  call void @llvm.lifetime.start.p0(i64 28, ptr nonnull %10)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %9)
  call void @llvm.lifetime.start.p0(i64 216, ptr nonnull %8)
  %389 = getelementptr inbounds %319, ptr %8, i64 0, i32 1
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %389, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %96) #32
  call void @llvm.lifetime.start.p0(i64 48, ptr nonnull %7)
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %7, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %124) #32
  call void @llvm.lifetime.start.p0(i64 48, ptr nonnull %6)
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %6, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %138) #32
  %390 = getelementptr inbounds %319, ptr %8, i64 0, i32 2
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %390, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %82) #32
  %391 = getelementptr inbounds %319, ptr %8, i64 0, i32 5
  store i64 1, ptr %391, align 8
  %392 = getelementptr inbounds %319, ptr %8, i64 0, i32 3
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(48) %392, ptr noundef nonnull align 8 dereferenceable(48) %7, i64 48, i1 false)
  store ptr null, ptr %8, align 8
  %393 = getelementptr inbounds %319, ptr %8, i64 0, i32 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(48) %393, ptr noundef nonnull align 8 dereferenceable(48) %6, i64 48, i1 false)
  call void @llvm.lifetime.end.p0(i64 48, ptr nonnull %6)
  call void @llvm.lifetime.end.p0(i64 48, ptr nonnull %7)
  call void @_ZN9mpl_utils5token3cpi14spl_token_burn17h4104af3a4b0840c1E(ptr noalias nocapture noundef nonnull sret(%244) dereferenceable(32) %9, ptr noalias nocapture noundef nonnull readonly dereferenceable(216) %8) #32
  call void @llvm.lifetime.end.p0(i64 216, ptr nonnull %8)
  call void @llvm.experimental.noalias.scope.decl(metadata !8114)
  %394 = load i32, ptr %9, align 8, !range !146, !alias.scope !8117, !noalias !8114, !noundef !4
  %395 = icmp eq i32 %394, 22
  br i1 %395, label %444, label %445

396:                                              ; preds = %387
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %19)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %18)
  call void @_ZN14solana_program12account_info17next_account_info17h843076ed74682877E(ptr noalias nocapture noundef nonnull sret(%20) dereferenceable(32) %18, ptr noalias noundef nonnull align 8 dereferenceable(32) %59) #32
  call void @llvm.experimental.noalias.scope.decl(metadata !8119)
  %397 = load i32, ptr %18, align 8, !range !146, !alias.scope !8122, !noalias !8119, !noundef !4
  %398 = icmp eq i32 %397, 22
  br i1 %398, label %399, label %408

399:                                              ; preds = %396
  %400 = getelementptr inbounds %22, ptr %18, i64 0, i32 1
  %401 = load ptr, ptr %400, align 8, !alias.scope !8122, !noalias !8119, !nonnull !4, !align !31, !noundef !4
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %18)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %19)
  %402 = load ptr, ptr %401, align 8, !nonnull !4, !align !37, !noundef !4
  %403 = call { i8, i8 } @_ZN14token_metadata10assertions4uses13assert_burner17hf2b7dbd81c686392E(ptr noalias noundef nonnull readonly align 1 dereferenceable(32) %402) #32
  %404 = extractvalue { i8, i8 } %403, 0
  %405 = and i8 %404, 1
  %406 = extractvalue { i8, i8 } %403, 1
  %407 = icmp eq i8 %405, 0
  br i1 %407, label %417, label %436

408:                                              ; preds = %396
  %409 = getelementptr inbounds i8, ptr %18, i64 4
  %410 = load i32, ptr %409, align 4, !alias.scope !8124
  %411 = getelementptr inbounds i8, ptr %18, i64 8
  %412 = load ptr, ptr %411, align 8, !alias.scope !8124
  %413 = getelementptr inbounds i8, ptr %18, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %19, ptr noundef nonnull align 8 dereferenceable(16) %413, i64 16, i1 false), !alias.scope !8124
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %18)
  %414 = getelementptr inbounds i8, ptr %0, i64 16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %414, ptr noundef nonnull align 8 dereferenceable(16) %19, i64 16, i1 false)
  store i32 %397, ptr %0, align 8, !alias.scope !8125
  %415 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %410, ptr %415, align 4, !alias.scope !8125
  %416 = getelementptr inbounds i8, ptr %0, i64 8
  store ptr %412, ptr %416, align 8, !alias.scope !8125
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %19)
  br label %241

417:                                              ; preds = %399
  call void @llvm.lifetime.start.p0(i64 64, ptr nonnull %17)
  %418 = call { ptr, i64 } @"_ZN91_$LT$solana_program..pubkey..Pubkey$u20$as$u20$core..convert..AsRef$LT$$u5b$u8$u5d$$GT$$GT$6as_ref17h56c78400b7ec32e8E"(ptr noalias noundef nonnull readonly align 1 dereferenceable(32) %1) #32
  %419 = extractvalue { ptr, i64 } %418, 0
  %420 = extractvalue { ptr, i64 } %418, 1
  call void @llvm.lifetime.start.p0(i64 1, ptr nonnull %16)
  store i8 %406, ptr %16, align 1
  store ptr @anon.3b777117c5a3ed67056920cb3eb2bd37.113, ptr %17, align 8
  %421 = getelementptr inbounds { ptr, i64 }, ptr %17, i64 0, i32 1
  store i64 8, ptr %421, align 8
  %422 = getelementptr inbounds [4 x { ptr, i64 }], ptr %17, i64 0, i64 1
  store ptr %419, ptr %422, align 8
  %423 = getelementptr inbounds [4 x { ptr, i64 }], ptr %17, i64 0, i64 1, i32 1
  store i64 %420, ptr %423, align 8
  %424 = getelementptr inbounds [4 x { ptr, i64 }], ptr %17, i64 0, i64 2
  store ptr @anon.3b777117c5a3ed67056920cb3eb2bd37.231, ptr %424, align 8
  %425 = getelementptr inbounds [4 x { ptr, i64 }], ptr %17, i64 0, i64 2, i32 1
  store i64 4, ptr %425, align 8
  %426 = getelementptr inbounds [4 x { ptr, i64 }], ptr %17, i64 0, i64 3
  store ptr %16, ptr %426, align 8
  %427 = getelementptr inbounds [4 x { ptr, i64 }], ptr %17, i64 0, i64 3, i32 1
  store i64 1, ptr %427, align 8
  call void @llvm.lifetime.start.p0(i64 28, ptr nonnull %15)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %14)
  call void @llvm.lifetime.start.p0(i64 216, ptr nonnull %13)
  %428 = getelementptr inbounds %319, ptr %13, i64 0, i32 1
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %428, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %96) #32
  call void @llvm.lifetime.start.p0(i64 48, ptr nonnull %12)
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %12, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %401) #32
  call void @llvm.lifetime.start.p0(i64 48, ptr nonnull %11)
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %11, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %138) #32
  %429 = getelementptr inbounds %319, ptr %13, i64 0, i32 2
  call fastcc void @"_ZN80_$LT$solana_program..account_info..AccountInfo$u20$as$u20$core..clone..Clone$GT$5clone17he2725f70e343ca4bE"(ptr noalias nocapture noundef nonnull sret(%3) dereferenceable(48) %429, ptr noalias noundef nonnull readonly align 8 dereferenceable(48) %82) #32
  %430 = getelementptr inbounds %319, ptr %13, i64 0, i32 5
  store i64 1, ptr %430, align 8
  %431 = getelementptr inbounds %319, ptr %13, i64 0, i32 3
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(48) %431, ptr noundef nonnull align 8 dereferenceable(48) %12, i64 48, i1 false)
  store ptr %17, ptr %13, align 8
  %432 = getelementptr inbounds { ptr, i64 }, ptr %13, i64 0, i32 1
  store i64 4, ptr %432, align 8
  %433 = getelementptr inbounds %319, ptr %13, i64 0, i32 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(48) %433, ptr noundef nonnull align 8 dereferenceable(48) %11, i64 48, i1 false)
  call void @llvm.lifetime.end.p0(i64 48, ptr nonnull %11)
  call void @llvm.lifetime.end.p0(i64 48, ptr nonnull %12)
  call void @_ZN9mpl_utils5token3cpi14spl_token_burn17h4104af3a4b0840c1E(ptr noalias nocapture noundef nonnull sret(%244) dereferenceable(32) %14, ptr noalias nocapture noundef nonnull readonly dereferenceable(216) %13) #32
  call void @llvm.lifetime.end.p0(i64 216, ptr nonnull %13)
  call void @llvm.experimental.noalias.scope.decl(metadata !8129)
  %434 = load i32, ptr %14, align 8, !range !146, !alias.scope !8132, !noalias !8129, !noundef !4
  %435 = icmp eq i32 %434, 22
  br i1 %435, label %440, label %441

436:                                              ; preds = %399
  %437 = icmp ult i8 %406, -52
  call void @llvm.assume(i1 %437)
  %438 = zext i8 %406 to i32
  store i32 0, ptr %0, align 8, !alias.scope !8134
  %439 = getelementptr inbounds i8, ptr %0, i64 4
  store i32 %438, ptr %439, align 4, !alias.scope !8134
  br label %241

440:                                              ; preds = %417
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %14)
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %15)
  call void @llvm.lifetime.end.p0(i64 1, ptr nonnull %16)
  call void @llvm.lifetime.end.p0(i64 64, ptr nonnull %17)
  br label %384

441:                                              ; preds = %417
  %442 = getelementptr inbounds i8, ptr %14, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %15, ptr noundef nonnull align 4 dereferenceable(28) %442, i64 28, i1 false), !alias.scope !8137
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %14)
  %443 = getelementptr inbounds i8, ptr %0, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %443, ptr noundef nonnull align 4 dereferenceable(28) %15, i64 28, i1 false)
  store i32 %434, ptr %0, align 8, !alias.scope !8138
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %15)
  call void @llvm.lifetime.end.p0(i64 1, ptr nonnull %16)
  call void @llvm.lifetime.end.p0(i64 64, ptr nonnull %17)
  br label %241

444:                                              ; preds = %388
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %9)
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %10)
  br label %384

445:                                              ; preds = %388
  %446 = getelementptr inbounds i8, ptr %9, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %10, ptr noundef nonnull align 4 dereferenceable(28) %446, i64 28, i1 false), !alias.scope !8142
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %9)
  %447 = getelementptr inbounds i8, ptr %0, i64 4
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(28) %447, ptr noundef nonnull align 4 dereferenceable(28) %10, i64 28, i1 false)
  store i32 %394, ptr %0, align 8, !alias.scope !8143
  call void @llvm.lifetime.end.p0(i64 28, ptr nonnull %10)
  br label %241

448:                                              ; preds = %384, %79
  ret void
}
