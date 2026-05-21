! Code base from Gemini implementing a k-d tree and searching it in fortran
! 21 May 2026

program test_global_map
    use kd_tree_mod
    implicit none
    ! RG:
    INTEGER, parameter :: nx = 4500
    INTEGER, parameter :: ny = 3298
    REAL :: lons(nx, ny), lats(nx, ny)

    !Gemini
    integer, parameter :: N = nx*ny
    type(GlobalGridNode), allocatable :: tree_nodes(:)
    integer, allocatable :: indices(:)
    integer :: root_node, best_node, i, j, k
    real :: query_lat, query_lon, query_xyz(3)
    real :: temp_xyz(3)

    allocate(tree_nodes(N))
    allocate(indices(N))

    ! 1. Mock up your nonuniform grid data
    ! Replace this loop with your actual file parsing/data stream ingestion
    !do i = 1, N
    !    ! Simulating random global points
    !    call random_number(query_lat) ! 0 to 1
    !    call random_number(query_lon) ! 0 to 1
    !    tree_nodes(i)%lat_lon(1) = (query_lat * 180.0) - 90.0   ! -90 to 90
    !    tree_nodes(i)%lat_lon(2) = (query_lon * 360.0) - 180.0  ! -180 to 180
    !    
    !    ! Pre-calculate 3D spatial points
    !    call lat_lon_to_3d(tree_nodes(i)%lat_lon(1), tree_nodes(i)%lat_lon(2), tree_nodes(i)%coord)
    !    
    !    tree_nodes(i)%payload%grid_id = i
    !    tree_nodes(i)%payload%value = 15.4 * i ! Sample payload data
    !    
    !    indices(i) = i ! Seed the indexing array
    !end do
    ! RG
    OPEN(FILE='rtofsll', FORM='UNFORMATTED', STATUS='OLD', unit=10)
    READ (10) lons
    READ (10) lats
    k = 0
    DO j = 1, ny
    DO i = 1, nx
      k = k + 1
      tree_nodes(k)%lat_lon(1) = lats(i,j)
      tree_nodes(k)%lat_lon(2) = lons(i,j)
      indices(k) = k

      ! Pre-calculate 3D spatial points
      call lat_lon_to_3d(tree_nodes(k)%lat_lon(1), tree_nodes(k)%lat_lon(2), tree_nodes(k)%coord)
     
      tree_nodes(k)%payload%grid_id = k
      tree_nodes(k)%payload%value = 15.4 * k ! Sample payload data
    ENDDO
    ENDDO
    !END RG


    ! 2. Build the Tree
    print *, "Building K-D Tree for RTOFS points..."
    root_node = build_global_kd_tree(tree_nodes, indices, 1, N, 0)
    print *, "Tree structural build finished! Root node is index: ", root_node

    ! 3. Search Example
    query_lat = 75.0
    query_lon = 170.0
    call lat_lon_to_3d(query_lat, query_lon, query_xyz)

    best_node = 0
    print *, "Querying closest grid point to Lat: 75.0, Lon: 170.0..."
    call find_nearest_global(tree_nodes, root_node, query_xyz, 0, best_node)

    print *, "--- NEAREST NEIGHBOR FOUND ---"
    print *, "Node Array Index: ", best_node
    print *, "Grid ID: ", tree_nodes(best_node)%payload%grid_id
    print *, "Actual Lat/Lon: ", tree_nodes(best_node)%lat_lon
    print *, "Data Value: ", tree_nodes(best_node)%payload%value

    deallocate(tree_nodes)
    deallocate(indices)
end program test_global_map
